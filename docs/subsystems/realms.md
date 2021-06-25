# Realms in Zulip

Zulip allows multiple *realms* to be hosted on a single instance.
Realms are the Zulip codebases's internal name for what we refer to in
user documentation as an organization (the name "realm" comes from
[Kerberos](https://web.mit.edu/kerberos/)).

Wherever possible, we avoid using the term `realm` in any user-facing
string or documentation; "Organization" is the equivalent term used in
those contexts (and we have linters that attempt to enforce this rule
in translateable strings).  We may in the future modify Zulip's
internals to use `organization` instead.

The
[production docs on multiple realms](../production/multiple-organizations.md)
are also relevant reading.

## Creating realms

There are two main methods for creating realms.

* Using unique link generator
* Enabling open realm creation

#### Using unique link generator

```bash
    ./manage.py generate_realm_creation_link
```

The above command will output a URL which can be used for creating a
new realm and an administrator user for that realm. The link expires
after the creation of the realm.  The link also expires if not used
within 7 days. The expiration period can be changed by modifying
`REALM_CREATION_LINK_VALIDITY_DAYS` in settings.py.

### Enabling open realm creation

If you want anyone to be able to create new realms on your server, you
can enable open realm creation.  This will add a **Create new
organization** link to your Zulip homepage footer, and anyone can
create a new realm by visiting this link (**/new**).  This
feature is disabled by default in production instances, and can be
enabled by setting `OPEN_REALM_CREATION = True` in settings.py.

## Subdomains

One can host multiple realms in a Zulip server by giving each realm a
unique subdomain of the main Zulip server's domain. For example, if
the Zulip instance is hosted at zulip.example.com, and the subdomain
of your organization is acme you can would acme.zulip.example.com for
accessing the organization.

For subdomains to work properly, you also have to change your DNS
records so that the subdomains point to your Zulip installation IP. An
`A` record with host name value `*` pointing to your IP should do the
job.

We also recommend upgrading to at least Zulip 1.7, since older Zulip
releases had much less nice handling for subdomains.  See our
[docs on using subdomains](../production/multiple-organizations.md) for
user-facing documentation on this.

### Working with subdomains in development environment

The default realm with the Shakespeare users has the subdomain `zulip`
and can be accessed by visiting <http://localhost:9991>.  Other realms
can be accessed at subdomains of localhost like
<http://analytics.localhost:9991>, which are supported by all modern
browsers.
