---
source: c:\EOTIR\EOTIR RPG\OOC\IPS\Plugins\(0A1) Installed Plugins\sslimageproxy-1.0.7\README.pdf
category: in_game_documents/diplomatic
/producer: Mac OS X 10.10.3 Quartz PDFContext
/creationdate: D:20150621180624Z00'00'
/moddate: D:20150621180624Z00'00'
source_type: EOTIR RPG
extraction_date: 2025-05-03T15:31:41.007044
---

1SSL Image Proxy - Installation Guide (c)2015 Jonathan Bennett / AutoIt Consulting Ltd https://www.autoitconsulting.com Verify Requirements Copy the ﬁle tools \ sslimageproxy_check.php ﬁle into your site root and ac-cess it from the web. Make sure all checks are passed before continuing to in-stallation. Installation Login to your Admin CP , and then go to System > Applications and click In-stall button. Browse to the the .tar ﬁle included with this distribution and install it. 

2Upgrading Login to your Admin CP , and then go to System > Applications. Find the application that you want to upgrade, click the arrow to show the dropdown menu and click Upload a new version. Browse to the the .tar ﬁle included with this distribution and upgrade it. Additional Tools Background Tasks There are some background tasks that can be queued in order to mass con-vert existing posts and content. Upload them from the tools folder into the root of your community (the place where init.php is located) and access them from your browser to start them. Delete them again after queueing:  - sslimageproxy_queue_rebuild_urls.php - This will go through all of your old posts and see if any images are suitable for rewriting to https. Any remaining http images will be converted to use the proxy.  -  sslimageproxy_ queue_remove_urls.php - This will go through all of your posts and remove the proxy urls and change them back to the originals. Use this if you wish to uninstall the application. 

3SSH/CLI Scripts There is a PHP command-line scripts available. Upload them from the tools folder into the root of your community (the place where init.php is located) and access them from SSH. Delete them again after use:  - sslimageproxy_cli_remove_proxy_urls.php - This will go through all of your posts and remove the proxy urls and change them back to the originals. Use this if you wish to uninstall the application. This script can be used after the application has been disabled. Help and Support Use this Marketplace topic 