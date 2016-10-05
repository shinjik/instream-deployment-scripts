import click
import sys
import json
import requests


def get_json(url):
    r = requests.get(url)
    return r.json()

def post_json(url, data=None):
    r = requests.post(url, data)
    return r.json()

def make_request(method, url, data=None):
    if data:
        r = requests.request(method, url, data=data)
    else:
        r = requests.request(method, url)
    if r.json():
        return r.json()
    else:
        raise RuntimeError

def list_apps(url):
    res = get_json(url + "/v2/apps")
    return res.get('apps', [])

@click.group()
@click.option('--url', type=str, help="Marathon instance base URL")
@click.pass_context
def cli(ctx, url):
    ctx.obj = url
    pass

@cli.command()
@click.pass_context
def list(ctx):
    res = list_apps(ctx.obj)
    for a in res:
        click.echo("\t%s | [%s] | [ %s of %s ] x [ %s CPU %s RAM %s disk ]" % 
            (   a['id'].ljust(28, ' '), 
                a['container']['docker']['image'].rjust(24, ' ') if a['container']['type'] == "DOCKER" else "container: %s" % a['container']['type'], 
                str(a['tasksRunning']).rjust(2, ' '),
                str(a['instances']).rjust(2, ' '), 
                str(a['cpus']).rjust(5, ' '), 
                str(a['mem']).rjust(5, ' '), 
                str(a['disk']).rjust(5, ' ')
            ))

@cli.command()
@click.option('--debug', is_flag=True, help="Dump all info")
@click.argument('id')
@click.pass_context
def info(ctx, id, debug):
    res = None
    try:
        res = make_request('GET', ctx.obj + "/v2/apps" + id)
        a = res['app']
        if res.get('message', None):
            click.echo("\t%[s]" % res['message'])
        click.echo("\t%s | [%s] | [ %s of %s ] x [ %s CPU %s RAM %s disk ]" % 
                (   a['id'].ljust(28, ' '), 
                    a['container']['docker']['image'].rjust(24, ' ') if a['container']['type'] == "DOCKER" else "container: %s" % a['container']['type'], 
                    str(a['tasksRunning']).rjust(2, ' '),
                    str(a['instances']).rjust(2, ' '), 
                    str(a['cpus']).rjust(5, ' '), 
                    str(a['mem']).rjust(5, ' '), 
                    str(a['disk']).rjust(5, ' ')
                )
            )
        click.echo("\tInstances:")
        for i in a['tasks']:
            click.echo("\t %s | %s | [%s]" %
                    (
                        i['state'].rjust(16),
                        i['host'].rjust(24),
                        ','.join(map(str, i['ports']))
                    )
                )
        click.echo("\t LB ports: %s" % ','.join(map(str, a['ports'])))
        if debug:
            click.echo(json.dumps(res, indent=4))
    except Exception:
        if isinstance(res, dict):
            click.echo("\t Error getting info: %s" % res['message'])
        else:
            click.echo("\t Unexpected runtime error occured")


@cli.command()
@click.argument('id')
@click.pass_context
def restart(ctx, id):
    res = post_json(ctx.obj + "/v2/apps" + id + '/restart')
    if res.get('message', None):
            click.echo("\t%[s]" % res['message'])
    ctx.invoke(info, id=id)

@cli.command()
@click.argument('id')
@click.pass_context
def delete(ctx, id):
    click.echo("\tAbout to delete app with id [%s]" % id)
    res = make_request('DELETE', ctx.obj + "/v2/apps" + id)
    if res.get('message', None):
            click.echo("\t%[s]" % res['message'])
    ctx.invoke(list)

@cli.command()
@click.option('--id', type=str, help="ID for the new app")
@click.option('--image', type=str, help="Docker image ID to spin from")
@click.option('--file', default=None)
@click.pass_context
def create(ctx, id, image, file):
    
    if file:
        ctx.invoke(create_from_file, file=file)

@cli.command()
@click.option('--file', default=None)
@click.pass_context
def create_from_file(ctx, file):
    click.echo("\tReading container definition from file specified")
    f = open(file, 'r')
    content = f.read()
    f.close()
    app_id = json.loads(content).get('id', None)
    if content and app_id:
        if app_id in [i['id'] for i in list_apps(ctx.obj)]:
            res = make_request('PUT', ctx.obj + "/v2/apps" + str(json.loads(content)['id']), content)
        else:
            res = make_request('POST', ctx.obj + "/v2/apps", content)
        if res.get('message', None):
            click.echo("\t[%s]" % res['message'])
        ctx.invoke(list)
    else:
        click.echo("No data read, aborting")
    

if __name__=="__main__":
    cli()