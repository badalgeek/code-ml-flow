## How to run database versioning.

```
alembic revision --autogenerate -m "Init database"
alembic upgrade head
```

## Assumption
* Read:Write ratio greater than 20:1
* * Most of the read traffic only reads the latest 20-40 comments of a repo.
Since keys in JSON will have high variance.(..??..)

## Database Schema

* User: Represents individual users of the system.
* GitAccount: Represents a user's account on a Git platform (e.g., GitHub, GitLab). Contains an authentication token.
* GitRepository: Represents a specific repository associated with a Git account which is added by the user.
* GitCommit: Represents individual commits made in a Git repository.
* MetricFile: Represents metric files associated with a specific commit.

## System Explained
* System will integrate with git providers using webhooks. Webhook will save the event. An async worker will pick unprocessed commit events, fetch metric file, flatten them, and save them in the database. If a webhook is not provided a poller will be required.
* When user adds a repo for the first time, an event will be added to the event table and an async worker will pick the event and process old commits in batches.

## Choices Explained:
Database Choice: 
* Postgres is chosen as database for small and mid scale. AWS Athena can scale up to 20 read replicas and 128 TB of data.
* Read Write ratio of this system exceeds 20:1 and reads don't require high consistency, which means db can be scaled using read replicas for reading and master for writing. 
* Since most of the users will only see top commits which means postgres caching will further improve the reads. In the read replica setting, the cache hit ratio can be boosted by using consistent hashing to send queries of one repo to one read replica. It's a very low effort since actually data won't be partitioned.

Table Choices:
* If MetricFile doesn't change. Commit will use the old entry of the metrics file which will save space.
* JSON file is stored after flattening the original JSON. This will allow simpler queries on metrics.
* Storing each key value as an individual row only makes sense if an index is created on the key. Since keys in JSON will have high variance, so index won't speed up the query. Since this table will have the largest amount of data, maintaining an index with high variance will slow down the DB over time.

Rough Scale Calculation:
* Number of orgs: 100
* Number of User: 100 * 20 = 2000
* Number of repos: 100 * 10 = 1000

* Commit per repos per day: 4
* Number of commits per day: 100 * 10 * 4 = 4000

* Avg size of metrics file per commit: 4KB
* Total data committed per day: 4000 * 4KB = 16 MB
* Total data committed per year: 4000 * 4KB * 365 = 5.8 GB

* Total read queries on metrics per user per day: 200
* Total read queries per day: 100 * 20 * 200 = 400000
* Total read queries per sec: 400000 / (24 * 3600) = 4.62

Future Scaling: Based on the above calculation even at a 10x scale postgres with read replica will be sufficient. Since Cloud provider DB is run on SSD, getting up to 50 QPS on multiple read replicas will not be a problem.

## Cons
* Since the system is storing everything on DB. There needs to be a limit in place that doesn't process the large file and shows a warning to the user that a few commits are missing because of file size. 

## Further Improvements
To reduce cost, support large metrics files and >10000 users. This system can be modified to reach the scale.

* The most cost-effective way is to use Postgres as an L1 cache and keep the first 20-40 commits on Postgres. 
* Use AWS Athena and save all the commits on S3 in parquet format(multiple commits need to be combined and stored to reduce files.).
* Most of the page views will hit the fast L1 cache on Postgres. Only order by queries and second-page queries will go to Athena.

