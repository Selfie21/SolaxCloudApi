# SolaxCloudApi
Has different functionalities most importantly getting the data from the Solax Cloud Portal. Gets your data from the Solax Cloud via the SolaxCrawler class. The Password has to be run through an MD5 hash (https://md5generator.de/).

If you want to verify the Certificate you have to install the Certificate from the solax site and refer to it in the verify param. Can't really do this since I am using it for my Alexa Skill.

Don't call the API to often, since it will get slowed down significantly. This isn't really a good way to access the Cloud anyway. But I guess since they don't have an API this is the best way.
