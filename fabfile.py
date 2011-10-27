from fabric.api import run, cd
from fabric.contrib.files import exists
from fabric.operations import sudo

def host_type():
    run('uname -s')

def install_packages():
    """ Install a bare minimum LAMP stack """
    run('apt-get install aptitude')
    run('aptitude update')
    run('aptitude upgrade')
    run('aptitude install libapache2-mod-php5 php5 php-pgsql git postgresql')

def deploy():
    """ Deploy our app by pulling it from github """
    
    # NOTE: Python's "with" statement is a "context manager". 
    # All the following commands  will be prefixed with "cd /path/to/  && "
    
    # Make sure our app directory exists.
    if not exists("/home/web/stupid-simple-php-app-for-fabric-demo/"):
        run("mkdir -p /home/web/")
        with cd("/home/web/"):
            run("git clone git://github.com/bradmontgomery/stupid-simple-php-app-for-fabric-demo.git")
    else: 
        with cd("/home/web/stupid-simple-php-app-for-fabric-demo"):
            # Fetch & Merge from the remote repo
            run('git pull git://github.com/bradmontgomery/stupid-simple-php-app-for-fabric-demo.git')

def set_file_permissions():
    """ Sets the appropriate read/execute permissions """
    with cd("/home/web/stupid-simple-php-app-for-fabric-demo/"):
        run("chmod -R 0755 app/")
        run("chown -R root:www-data app/")

def set_apache_config():
    """ Replace's apache's default config file """
    # Delete the existing default config file.
    if exists("/etc/apache2/sites-enabled/000-default"):
        run("rm /etc/apache2/sites-enabled/000-default")

    with cd("/etc/apache2/sites-enabled/"):
        run("ln -s /home/web/stupid-simple-php-app-for-fabric-demo/apache/000-default .")
        run("apachectl restart")

def backup():
    """ Make a tarball snapshot of the deployed codebase """
    with cd("/home/web/"):
        run("tar -czf /root/stupid-simple-php-app-for-fabric-demo.tgz stupid-simple-php-app-for-fabric-demo/")

def revert():
    """ Revert the codebase from a backup """
    if exists("/root/stupid-simple-php-app-for-fabric-demo.tgz"):
        with cd("/home/web/"):
            run("tar -xzf /root/stupid-simple-php-app-for-fabric-demo.tgz")

def db_setup():
    """ set up a new database """
    # Symlink our own config file and restart PostgreSQL
    with cd("/etc/postgresql/8.4/main/"):
        # remove the existing config file
        if exists("pg_hba.conf"): 
            run("rm pg_hba.conf")
        run("ln -s /home/web/stupid-simple-php-app-for-fabric-demo/db/pg_hba.conf pg_hba.conf")
        run("/etc/init.d/postgresql restart")
    
    # Create a superuser named "dbuser" and prompt for a password
    sudo("createuser -s -P dbuser", user="postgres")
    # Create a dabase named "appdb" owned by "dbuser"
    sudo("createdb -E UTF8 -O dbuser -T template0 appdb", user="postgres")
    # Run SQL from a file
    run("psql -U dbuser -d appdb -f /home/web/stupid-simple-php-app-for-fabric-demo/db/db.sql")

