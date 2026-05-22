
  /var/cache/test/README.md
  Guilherme Lima

I use this directory (/var/cache/test) as a repository for useful
debugging bash and python scripts, that I can easily modify for
debugging purposes.

In particular, I always copied the followed files to a brand new
consistency pod, as they were useful in my daily monitoring of the
consistency system in general:

.bashrc - defines useful aliases and env variables.  I always source
          it whenever I login into the pod: source
          /var/cache/test/.bashrc

suggest - From the RSE name, it suggests command lines to submit
          consistency jobs manually for each site, using nohup and
          redirecting its output, so the logs are saved even if I
          immediately logout from the pod.  Usage: suggest
          T3_US_Colorado T2_BR_UERJ ...  -> then copy and paste the
          commands into the CLI

The following scripts are helpful to test just a single component of
the CE system, usually using existing data rather than starting a new
scan, etc.

  test-dark.sh
  test-missing.sh
  test-merge-config.sh
  testscan-site_cmp3.sh

# 

The following can be easily edited to run single components interactively, while
the output is redirected into the /var/cache/test/ area for analysis without
interfering with the data displayed by the monitoring pages
(https://cmsweb.cern.ch/rucioconmon/ce/index)

  run-testscan
  run-rcescan
  run-xrootd <-- xrootd scanner
  run-gfal   <-- gfal-ls scanner - see below


Regarding the gfal-https project, I managed to create a running scanner based on
gfal-ls, which I tested on the pod itself after *manually installing* gfal for my
tests.

I got lots of good info and tips from AI (e.g. https://gemini.google.com/app).
I installed these packages:

   dnf install gfal2
   dnf install -y epel-release
   dnf update
   dnf install -y gfal2-util-scripts gfal2.plugin-http gfal2.plugin-xrootd
   dnf clean all
   rm -rf /var/cache/dnf

### Using gfal-ls in CalTech: server: k8s-transfer-15.ultralight.org:1094
gfal-ls root://hepxrd01-colorado.sites.opensciencegrid.org:1094/store/relval
gfal-ls https://hepxrd01-colorado.sites.opensciencegrid.org:1094/store/relval


I managed to create a gfal_client.py and a modified version of xrootd_scanner.py
that uses it.  XRootd is still used by default, but adding a `-g` option to the
`python3 xroot_scanner.py` call will trigger the use of GFALClient class.

Unfortunately, I also found that gfal does not have a recursive listing option
(e.g. gfal-ls -R), therefore the roots have to be scanned in flat-mode, and the
subdirectories are queued for subsequent processing.  The whole processing ends
up being a lot slower than xrootd protocol.

You can immediately try it until the current pod is restarted, by doing:

  -> login to the consistency pod, then:
  source /var/cache/test/.bashrc
  cd /var/cache/test

  . ./run-xrootd   (this takes about 2min for Colorado)
  . ./run-gfal     (this takes about 20min for Colorado, and returns less files than xrootd)

I hope this is helpful!
Please let me know if any questions.
