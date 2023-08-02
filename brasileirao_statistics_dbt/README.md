Welcome to your new dbt project!

### Using the starter project

Try running the following commands:
- dbt run
- dbt test


## Sample of the profiles.yml

```yml
brasileirao_statistics:
  target: stage
  outputs:
    stage:
      type: postgres
      host: localhost
      user: myuser
      password: mypassword
      port: 5432
      dbname: raw_soccer
      schema: raw_data
```

### Resources:
- Learn more about dbt [in the docs](https://docs.getdbt.com/docs/introduction)
- Check out [Discourse](https://discourse.getdbt.com/) for commonly asked questions and answers
- Join the [chat](https://community.getdbt.com/) on Slack for live discussions and support
- Find [dbt events](https://events.getdbt.com) near you
- Check out [the blog](https://blog.getdbt.com/) for the latest news on dbt's development and best practices
