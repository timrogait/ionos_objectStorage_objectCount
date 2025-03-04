# ionos_objectStorage_objectCount
simple Python UI to show amount of objects in IONOS object storage buckets

This script allows to display data of IONOS object storage buckets including

bucket name
number of objects
number of versioning objects including deletion markers
location of the bucket
if versioning and / or object lock is enabled

A valid access and secret access key must be provided to load the buckets.
Multiple buckets can be selected or the "all buckets" option can be used.
Note: approx. 300k files can be counted per minute. If you are using buckets with a lot of objects, it is adviced to select them one by one.
