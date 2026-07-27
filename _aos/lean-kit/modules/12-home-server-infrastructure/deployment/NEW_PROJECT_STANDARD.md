# New AOS Project Server Deployment Standard
# V321-WP-SERVER-GITOPS | Mandatory for all projects from V321+

## Steps (in order)

1. Register ports in port-registry.yaml (team_60 + team_100 + team_00 sign-off)
2. git init --bare /data/repos/{id}.git
3. git clone {source} /data/projects/{id}
4. Write /data/projects/{id}/.env (never in git)
5. Write /etc/systemd/system/{id}.service (if has API runtime)
6. systemctl enable --now {id}
7. Write /data/repos/{id}.git/hooks/post-receive (chmod 755)
8. Add nginx server block to /etc/nginx/sites-available/aos-ecosystem (if has web UI)
9. nginx -t && systemctl reload nginx
10. Add backup entry to /data/scripts/aos-backup.sh (if has DB)
11. Mac: git remote add waldhome nimrodw@100.125.98.56:/data/repos/{id}.git

## Verification
curl http://127.0.0.1:{PORT}/health   # API health — MUST expose git_sha (DV-1)
git push waldhome main                 # Mac deploy test

## Deploy verification (BINDING — see DEPLOY_VERIFICATION_CANON_v1.0.0.md)
A deploy is GREEN only when prod STATE is asserted (DV-1): `/health` `git_sha` == pushed SHA **and**
`readlink /opt/{id}/current` == intended `releases/<tag>`. NEVER declare success on a hook/ssh exit code or a
"DEPLOY OK" log line. Use the release-symlink mechanism (`releases/<tag>` + atomic `current` flip + auto-rollback);
the `post-receive` hook delegates to it — never a parallel working-clone reset (DV-2). Reference model:
`TikTrack-Phoenix_AOSProject/scripts/deploy-staging.sh`. Full rules: `DEPLOY_VERIFICATION_CANON_v1.0.0.md`.
