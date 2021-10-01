# Deploying Screaming Frog on Google Cloud Platform

This repo contains the basic set up and deploy scripts to run Screaming Frog using Google Cloud Platform's Compute Engine. Multiple instances of Screaming Frog can be deployed to crawl large sites or lists of URLs.  Google Compute Engine VMs can be deployed for one-time crawls or scheduled as needed for on-going crawling and analysis of the same site or list of URLs.

Screaming Frog crawl data can be exported directly to Google Drive or to BigQuery for additional processing and analysis.

Deploying Screaming Frog on GCP virtual machines enables large-scale repeatable site crawling from reliable infrastructure. Virtual machines can be configured as needed for large sites and crawl data can be processed in BigQuery. Crawls can also be exported using Screaming Frog's crawl format to Google Drive and then downloaded for additional analysis on local machines using the Screaming Frog interface.

## Requirements

- [Screaming Frog license](https://www.screamingfrog.co.uk/seo-spider/)
- Google Cloud Platform and Compute Engine access
- (optional) Google Drive and BigQuery access to export data

## Guide
- Configure Compute Engine Virtual Machine instance
- Install Screaming Frog and crawl scripts
- Create machine image
- Deploy Screaming Frog crawl VMs from your machine

### Configure Compute Engine

First you'll need to set up a virtual machine instance in [GCP Compute Engine](https://cloud.google.com/compute). If you haven't already - create a GCP account and project and then enable the Compute Engine API. Costs may vary depending on machine and memory size as well as any additional charges for BigQuery, Cloud Storage, or other cloud products.

Once you've got your GCP project set up you can begin creating a virtual machine.

![Configuring GCP Virtual Machine](https://github.com/myawesomebike/SF-CLI-GCP/raw/master/vm-config.png)

Give your VM a relevant name and select a region near the site that you're planning to crawl. This cuts down on request time and latency when crawling larger sites. You may be able to find where a site is hosted via a `WHOIS` lookup or similar.

Make sure to select a machine with enough memory to crawl the site or URL list you're using. You may need to run Screaming Frog locally to determine how much memory you need. If your VM runs out of memory it will likely crash or reset which typically results in a loss of crawl data.  It is not recommended to use many threads when crawling a site with Screaming Frog so you may not need a virtual machine with many CPUs.

If you plan on rendering site content you may want to enable a display device as it's typically a required dependency for some rendering engines.  Consider using a [private instance of WebPageTest](https://docs.webpagetest.org/private-instances/) if you're planning on rendering content with multiple devices or want to capture detailed page loading information for site speed analysis, device support, or other rendering workflows.

Select a boot disk that's large enough to store your crawl data. You may need more space if using Screaming Frog database storage mode.  You'll also need to include enough disk space for any data that you're exporting - even if using BigQuery. Screaming Frog data must first be exported to CSV format on the virtual machine before it can be written to BigQuery.

Screaming Frog runs on Ubuntu so select a compatible Ubuntu image for the Screaming Frog version you're using.

You'll need to make sure your virtual machine has access to the relevant Google Cloud API scopes so it can write Google Drive and Google BigQuery data.

Lastly you'll need to make sure your virtual machine has HTTP and HTTPS traffic access to crawl your target sites.

Once your virtual machine is configured you can create it and start setting up Screaming Frog.

### Setting up Screaming Frog on your virtual machine

After creating your VM you can start and SSH into the VM console to begin configuring Screaming Frog. You'll be using the Ubuntu version of Screaming Frog in headless/command line mode to crawl sites.  You may need the desktop version to set up any custom configurations including content extraction or other crawling rules which you can then upload to the VM.

**Install wget**

If your VM does not already have `wget` you can install it using `apt`.  You'll use `wget` to download Screaming Frog and get the crawling shell script.
```console
sudo apt-get install wget
```

**Download Screaming Frog**

Get the latest Ubuntu version of [Screaming Frog](https://www.screamingfrog.co.uk/seo-spider/release-history/) and download it to the virtual machine using `wget` in your `~` user directory.
```console
cd ~
wget -c https://download.screamingfrog.co.uk/products/seo-spider/screamingfrogseospider_16.1_all.deb
```

**Install Screaming Frog**

Install Screaming Frog and any dependencies using `apt`.
```console
sudo apt install ./screamingfrogseospider_16.1_all.deb
```

**Add Screaming Frog config and license**

Move to the Screaming Frog config folder and create a new `spider.config` file.
```console
cd ~/.ScreamingFrogSEOSpider
nano spider.config
```

Add the following line to accept the Screaming Frog end user license agreement and save.
```text
eula.accepted=11
```

Next create the license file in the same directory.
```console
nano license.txt
```

Add your user name and license in the file and save.
```text
_screaming-frog-user-name_
_license-key_123456_
```

Then create the `crawl-data` directory in your user directory to store the exported crawl data CSVs.
```console
mkdir crawl-data
```

Get the `cloudcrawl.sh` script from the `SF-CLI-GCP` repo. This shell script sets up the Screaming Frog crawl and exports the crawl data to BigQuery. You can run this script for ad hoc crawls and use it as a start up script when scheduling or deploying Screaming Frog virtual machines.

```console
wget https://raw.githubusercontent.com/myawesomebike/SF-CLI-GCP/master/cloudcrawl.sh
```

You can customize what data Screaming Frog exports in the `cloudcrawl` script. You'll need to clean up each CSV before uploading the relevant data to BigQuery. You can also configure the `cloudcrawl` script to send a notification when the crawl is completed or shut down the VM if it is no longer needed (see deploy section).

## Create Machine Image

Once your Screaming Frog VM has been set up and configured you can create an image of that VM machine to deploy over and over.  You can set up a VM to crawl the same site on a scheduled basis to detect changes, new content, and other important updates. VM images can also deployed for one-time use quickly and easily by setting the site in the instance deploy script (see deploy section)

Select your VM in the Compute Engine Instances view.

![GCP VM Instances](https://github.com/myawesomebike/SF-CLI-GCP/raw/master/create-machine-image.png)

Create a new machine image based on the VM you just created. You'll be able to deploy this machine image locally or from other GCP services such as App Engine or Cloud Scheduler.

![GCP Machine Image](https://github.com/myawesomebike/SF-CLI-GCP/raw/master/create-vm-image.png)

## Deploy your Screaming Frog virtual machines

Once you've configured your Screaming Frog virtual machine and made an image of that VM you can now deploy that image to crawl your target sites.

### Using GCP Console

You can create as many virtual machines from your images by creating a new VM from a machine image.  You'll be able to adjust the VM's location and type if you need a different region or a VM with more memory.

Once created you'll need to SSH into your VM to start the crawl manually using the `cloudcrawl` bash script.

```console
cd ~
bash cloudcrawl.sh
> Enter domain to crawl
_www.example.com_
```

Screaming Frog will start crawling your site and upon completion it will save the configured crawl data and upload it to BigQuery.  If you maintain your SSH session you'll be able to monitor crawl progress and review any error output from Screaming Frog as well as interupt the VM if the crawl is taking too long.

### Using Google Compute APIs

You can run `createinstance.py` to create a new VM from your Screaming Frog VM image.  You'll need to create a service account and add the service account file to your local directory to authorize all requests to the `googleapiclient`. You'll also need to set your service account information in the `config` settings.

You'll need to customize the `machine` and `snapshot` variables in `createinstance.py` for your preferred machine settings and VM image snapshot location.

You can set the target site to crawl in the `startupscript` variable.  When the virtual machine is created and started the `startupscript` will get called to set up the crawl using the `cloudcrawl` bash script you set up earlier.

You can quickly create as many virtual machines for each site you're planning to crawl. You can persist these VMs for as long as needed and simply restart them to recrawl the configured site that you set in the `startupscript`.
