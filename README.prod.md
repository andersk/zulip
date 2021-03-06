This documents the process for installing Zulip in a production environment.

Recommended requirements:

* Server running Ubuntu Precise or Debian Wheezy
* At least 2 CPUs for production use
* At least 4GB of RAM for production use
* At least 100GB of free disk for production use
* HTTP(S) access to the public Internet (for some features;
  discuss with Zulip Support if this is an issue for you)
* SSL Certificate for the host you're putting this on
  (e.g. https://zulip.example.com)
* Email credentials for the service to send outgoing emails to users
  (e.g. missed message notifications, password reminders if you're not
  using SSO, etc.).

=======================================================================

How to install Zulip in production:

These instructions should be followed as root.

(1) Install the SSL certificates for your machine to
  /etc/ssl/private/zulip.key
  and
  /etc/ssl/certs/zulip.combined-chain.crt

(2) download zulip-server.tar.gz, and unpack to it /root/zulip, e.g.
tar -xf zulip-server-1.1.3.tar.gz
mv zulip-server-1.1.3 /root/zulip

(3) run /root/zulip/scripts/setup/install

This may take a while to run, since it will install a large number of
packages via apt.

(4) Configure the Zulip server instance by filling in the settings in
/etc/zulip/settings.py

(5) su zulip -c /home/zulip/deployments/current/scripts/setup/initialize-database

This will report an error if you did not fill in all the mandatory
settings from /etc/zulip/settings.py.  Once this completes
successfully, the main installation process will be complete, and if
you are planning on using password authentication, you should be able
to visit the URL for your server and register for an account.

(6) Subscribe to
https://groups.google.com/forum/#!forum/zulip-announce to get
announcements about new releases, security issues, etc.

=======================================================================

Maintaining Zulip in production:

* To upgrade to a new version, download the appropriate release
  tarball from https://www.zulip.org, and then run as root

  /home/zulip/deployments/current/scripts/upgrade-zulip <tarball>

  The upgrade process will shut down the service, run `apt-get
  upgrade` and any database migrations, and then bring the service
  back up.  This will result in some brief downtime for the service,
  which should be under 30 seconds unless there is an expensive
  transition involved.  Unless you have tested the upgrade in advance,
  we recommend doing upgrades at off hours.

  You can create your own release tarballs from a copy of this
  repository using `tools/build-release-tarball`.

* To update your settings, simply edit /etc/zulip/settings.py and then
  run /home/zulip/deployments/current/scripts/restart-server to
  restart the server

* You are responsible for running "apt-get upgrade" on your system on
  a regular basis to ensure that it is up to date with the latest
  security patches.

* To use the Zulip API with your Zulip server, you will need to use the
  API endpoint of e.g. "https://zulip.yourdomain.net/api".  Our Python
  API example scripts support this via the
  "--site=https://zulip.yourdomain.net" argument.  The API bindings
  support it via putting "site=https://zulip.yourdomain.net" in your
  .zuliprc.

* Similarly, you will need to instruct your users to specify the URL
  for your Zulip server when using the Zulip desktop and mobile apps.

* As a measure to mitigate the impact of potential memory leaks in one
  of the Zulip daemons, the service automatically restarts itself
  every Sunday early morning.  See /etc/cron.d/restart-zulip for the
  precise configuration.


=======================================================================

SSO Authentication:

Zulip supports integrating with a corporate Single-Sign-On solution.
There are a few ways to do it, but this section documents how to
configure Zulip to use an SSO solution that best supports Apache and
will set the REMOTE_USER variable:

(0) Check that /etc/zulip/settings.py has
"zproject.backends.ZulipRemoteUserBackend" as the only enabled value
in the "AUTHENTICATION_BACKENDS" list, and that "SSO_APPEND_DOMAIN" is
correct set depending on whether your SSO system uses email addresses
or just usernames in REMOTE_USER.

Make sure that you've restarted the Zulip server since making this
configuration change.

(1) Edit /etc/zulip/zulip.conf and change the puppet_classes line to read:

puppet_classes = zulip::enterprise, zulip::apache_sso

(2) As root, run

/home/zulip/deployments/current/scripts/zulip-puppet-apply

to install our SSO integration.

(3) To configure our SSO integration, edit
/etc/apache2/sites-available/zulip-sso.example and fill in the
configuration required for your SSO service to set REMOTE_USER and
place your completed configuration file at

/etc/apache2/sites-available/zulip-sso

(4) Run

a2ensite zulip-sso

To enable the Apache integration site.

Now you should be able to visit https://zulip.yourdomain.net/ and
login via the SSO solution.
