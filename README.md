## How to run database versioning.

```
alembic revision --autogenerate -m "Init database"
alembic upgrade head
```

## Assumption
Read:Write ratio greater than 20:1
Most of the read traffic only reads latest 20-40 comments of a repo.
Since keys in json will have high varience.(..??..)

## Databse Schema

User: Represents individual users of the system.
GitAccount: Represents a user's account on a Git platform (e.g., GitHub, GitLab). Contains authentication token.
GitRepository: Represents a specific repository associated with a Git account which is added by user.
GitCommit: Represents individual commits made in a Git repository.
MetricFile: Represents metric files associated with a specific commit.

## System Explained
* System will integrate with git providers using webhooks. Webhook will save the event. An async worker will pick unprocessed commit event, fetch metrics file, flatten them and save in database. If webhook is not provided a poller will be required.
* When user add a repo for first time, an event will be added in event table and async worker will pick the event and process old commits in batches.

## Choices Explained:
Database Choice: 
* Postgres is chosen as database for small and mid scale. AWS Athena can scale upto 20 read replica and 128 TB of data.
* Read Write ratio of this system exceed 20:1 and reads doesn't require high consistency, which means db can be scaled using read replicas for reading and master for writing. 
* Since most of the user will only see top commits which means postgres caching will further improve the reads. In read replica setting, cache hit ratio can be boosted by using consistent hasing to send queryies of one repo to one read replica. It's a very low effort since actually data won't be partitioned.

Table Choices:
* If MetricFile doesn't change. Commit will use the old entry of metrics file which will save space.
* Json file is stored after flattening the original json. This will allow simpler queries on metrics.
* Storing each key value as individual row only make sense if an index is created on key. Since keys in json will have high varience, so index won't speed up the query. Since this table will have largest amount of data, mantaining a index with high varience will slow down the DB over time.

Rough Scale Calculation:
Number of orgs: 100
Number of User: 100 * 20 = 2000
Number of repos: 100 * 10 = 1000

Commit per repos per day: 4
Number of commits per day: 100 * 10 * 4 = 4000

Avg size of metrics file per commit: 4KB
Total data commited per day: 4000 * 4KB = 16 MB
Total data commited per year: 4000 * 4KB * 365 = 5.8 GB

Total read queries on metrics per user per day: 200
Total read queries per day: 100 * 20 * 200 = 400000
Total read queries per sec: 400000 / (24 * 3600) = 4.62

Future Scaling: Based on above calculation even at 10x scale postgres with read replica will be sufficient enough. Since Cloud provider DB are run on SSD, hence getting upto 50 QPS on multiple read replica will be not be a problem.

## Cons
* Since system is storing everting on DB. There need to be limit in place which doesn't process large file and show a warning to user that few commits are missing because of file size. 

## Further Improvements
To reduce cost, support large metrics file and >10000 users. This system can be modified to reach the scale.

Most cost effective way is to use Postgres as L1 cache and keep first 20-40 commits on postgres. 
Use AWS Athena and save all the commit on S3 in parquet format(multiple commit need to be combined and stored to reduce files.).
Most of the page views will hit fast L1 cache on postgres. Only order by queries and second page query will go to athena.

