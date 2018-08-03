<p align=center><img align=center src'logo.png' width=200 /></p>
<h3 align=center>fup</h3>
<h6 align=center>fPlease UPload it!</h6>

## Usage

```shell
$ fup init myapp
Creating new app [myapp]...
Success!
```

```shell
$ fup list
Targets pending deploy:
- myapp
Available deploy targets:
- dev
- production
- integration
- jordans-test-branch
```

```shell
$ fup deploy myapp
Deploying...
Success!
Your application is available at:
API:    https://...
Web:    https://...
DB:     aws://...
```

```shell
$ fup deploy myapp
Deploying...
Failed! This application has already been deployed. Did you mean [update]?
```

```shell
$ fup update myapp
Updating [db,web,api]...
Success!
```

```shell
$ fup update myapp db
Updating [db]...
Success!
```


```shell
$ fup status myapp
Your application is available at:
API:    https://...
Web:    https://...
DB:     aws://...
```
