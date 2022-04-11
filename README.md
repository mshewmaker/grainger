
----------------
0.  General Goal
----------------

Return a US state given a two-character state code, via a scalable API that's automatically provisioned using containers.

----------------------------------------------------------------
1.  DNS solution:  Find the name of a state by doing a DNS query
----------------------------------------------------------------

With some unused domains laying around, I couldn't resist putting one
to use as a sample solution.

    $ host -t txt nc.dns.pondernation.com
    nc.dns.pondernation.com descriptive text "North Carolina"
    $ host -t txt ak.dns.pondernation.com
    ak.dns.pondernation.com descriptive text "Alaska"
    $ host -t txt DC.dns.pondernation.com
    DC.dns.pondernation.com descriptive text "District of Columbia"
    $ host -t txt nonexistent.dns.pondernation.com
    nonexistent.dns.pondernation.com has no TXT record

This DNS-based solution doesn't use containers, but DNS automatically scales
and caches data horizontally across a population.

If millions of people were doing a bunch of small queries like this
for a small set of data that rarely changed often, this would be an potential
solution.

To deploy:

    $ cd dns
    $ create config.py based on filled-in version of config_EDITME.py
    $ ./state_dns_solution.py

Note that I didn't include proper secrets management.

--------------------------------
2.  Cloud function HTTP solution
--------------------------------

This solution involves containers, but you don't need to explicitely work with them.

Also, this solution scales down to zero containers in use if the system isn't busy.

Example query and output:

    $ curl https://us-central1-playground-s-11-8de871e6.cloudfunctions.net/states/ga
    Georgia
    $ curl https://us-central1-playground-s-11-8de871e6.cloudfunctions.net/states/ca
    California
    $ curl https://us-central1-playground-s-11-8de871e6.cloudfunctions.net/states/oh
    Ohio
    $ curl https://us-central1-playground-s-11-8de871e6.cloudfunctions.net/states/dc
    District of Columbia
    $ curl https://us-central1-playground-s-11-8de871e6.cloudfunctions.net/states/nonexistent
    Unrecognized state code

To deploy:

    $ cd cloudfunctions/
    $ gcloud functions deploy states --runtime python39 --trigger-http --allow-unauthenticated --entry-point=process_request --memory=128MB --security-level=secure-optional --timeout=5s --max-instances=10
    $ gcloud functions describe states

The output of the gcloud command includes a "url: " entry that points to
a URL for use in curl tests such as given above.

Note:  In the gcloud command, I set max-instances to 10 simply because this is a test instance.

-------------------------------------------------
3.  Cloud Run HTTP solution - deployed via gcloud
-------------------------------------------------

    $ cd cloudrun-gcloud
    $ gcloud run deploy states --source ./ --region=us-east1
    $ gcloud run services describe states --region=us-east1|grep URL:

Both gcloud commands show the URL to use to do the query.  You'd grep them
the same way, but it's easier to visually see in the second gcloud command.


----------------------------------------------------
4.  Cloud Run HTTP solution - deployed via terraform
----------------------------------------------------

    $ cd cloudrun-tf

Create repository with:

    $ gcloud artifacts repositories create docker-repo --repository-format=docker --location=us-central1 --description="Docker repository"

Verify with:

    $ gcloud artifacts repositories list

Submit for build

    $ PROJECT=$(gcloud config get-value project)
    $ gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT/docker-repo/states-image:tag1

    $ vim main.tf # update project and image values.  Yes..I could fix that.
    $ terraform plan
    $ terraform apply

    Note that the code, dockerfile, and requirements for both Cloud Run solutions are the same.

------------------------
5.  Potential extensions
------------------------

    1.  Including proper secrets management
    2.  Add configuration of when scaling is needed
    3.  Fix the need to update the project name in the cloud run main.tf
    4.  Update a CNAME in cloudflare for each of the three non-DNS
        solutions, so there's a nice URL instead of a random playground
        URL for the queries.  That could be done in python as in the DNS
        solution, or via terraform, (there's a cloudflare provider).
        
