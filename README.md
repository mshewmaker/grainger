
## 0.  General Goal

Return a US state given a two-character state code, via a scalable API that's automatically provisioned using containers.

## 1.  Initialization:

On creating a new GCP sandbox or project:

    $ gcloud init
    $ gcloud auth application-default login
    $ export TF_VAR_project_id=$PROJECT_ID
    $ export PROJECT_ID=$(gcloud config get-value project)

Then enable API access with

    $ cd enable-gcp-apis
    $ # rm terraform.tfstate terraform.tfstate.backup  # Do only if recreating google sandbox
    $ terraform init

## 2.  DNS solution:  Find the name of a state by doing a DNS query

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
for a small set of data that rarely changed often, this would be a potential
solution.

To deploy:

    $ cd dns
    $ test -f config.py || cp -a config_dist.py config.py
    $ vim config.py # Enter appropritate cloudflare and domain info
    $ ./state_dns_solution.py

Note that I didn't include proper secrets management.

## 3.  Cloud function HTTP solution

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
    $ gcloud functions describe states | grep url:

(The output of both gcloud commands include a "url: " entry that points to
a URL for use in curl tests such as given above.)

Note:  In the gcloud command, I set max-instances to 10 simply because this is a test instance.

## 4.  Cloud Run HTTP solution - deployed via gcloud

Example queries and output:

    $ curl https://states-nuwse2zczq-ue.a.run.app/state/ga/
    Georgia
    $ curl https://states-nuwse2zczq-ue.a.run.app/state/dc/
    District of Columbia
    $ curl https://states-nuwse2zczq-ue.a.run.app/state/fl/
    Florida
    $ curl https://states-nuwse2zczq-ue.a.run.app/state/oh/
    Ohio
    $ curl https://states-nuwse2zczq-ue.a.run.app/state/nonexistent/
    Unrecognized state code

To deploy:

    $ cd cloudrun-gcloud
    $ gcloud run deploy states --source ./ --region=us-east1 --allow-unauthenticated
    $ gcloud run services describe states --region=us-east1|grep URL:

## 5.  Cloud Run HTTP solution - deployed via terraform

Example queries and output:

    $ curl https://states-nuwse2zczq-uc.a.run.app/state/ga/
    Georgia
    $ curl https://states-nuwse2zczq-uc.a.run.app/state/il/
    Illinois
    $ curl https://states-nuwse2zczq-uc.a.run.app/state/ok/
    Oklahoma
    $ curl https://states-nuwse2zczq-uc.a.run.app/state/dc/
    District of Columbia
    $ curl https://states-nuwse2zczq-uc.a.run.app/state/nonexistent/
    Unrecognized state code

    $ cd cloudrun-tf

Create repository with:

    $ gcloud artifacts repositories create docker-repo --repository-format=docker --location=us-central1 --description="Docker repository"

Verify with:

    $ gcloud artifacts repositories list

Submit for build:

    $ PROJECT=$(gcloud config get-value project)
    $ gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT/docker-repo/states-image:tag1

    $ vim main.tf

Before first run only: 

    $ # rm terraform.tfstate terraform.tfstate.backup  # Do only if recreating google sandbox
    $ terraform init

Then on every change:

    $ terraform plan  -var="container_image=ENTER_IMAGE_HERE"
    $ terraform apply -var="container_image=ENTER_IMAGE_HERE"

Note that the code, dockerfile, and requirements for both Cloud Run solutions are the same.

## 6.  Potential extensions

    1.  Including proper secrets management
    2.  Add configuration of when scaling is needed
    3.  Update a CNAME in cloudflare for each of the three non-DNS
        solutions, so there's a nice URL instead of a random playground
        URL for the queries.  That could be done in python as in the DNS
        solution, or via terraform, (there's a cloudflare provider).

