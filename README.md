# Mark extra feedly item as read

* Mark duplicate url items
* Mark ads item

#### deploy

1. set up apex http://apex.run/
2. execut init to create iam role. input project name you like.
```
apex init
```
3. remove created `hello` project.
4. execute apex like this:
```
apex deploy -s REFRESH_TOKEN=... -s CLIENT_SECRET=...
```
5. set CloudWatch if you want to execute constantly.

#### get refresh token

[https://developer.feedly.com/v3/auth/](https://developer.feedly.com/v3/auth/)
