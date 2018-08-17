# coding: utf-8
import click
import os
from imutils import paths
from src.generate_captcha import generate
from src.extract_captcha import extract
from src.train_model import train
from src.predict_model import predict


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("Simple Captcha Solver v0.01")
    ctx.exit()

@click.group()
@click.option("--version", is_flag=True, callback=print_version, expose_value=False, is_eager=True)
@click.option('--debug', is_flag=True, default=False)
def cli(debug):
    click.echo('Debug mode is %s' % ('on' if debug else 'off'))


@cli.command(help="Captchas Generator")
@click.option("-o", help="captchas output path", default='tmp/generate')
@click.option("-n", help="generated captchas count", default=10000)
@click.option("-c", help="captchas code length", default=4)
def start_generate(o, n, c):
    generate(generate_dir=o, total=n, code_length=c)


@cli.command(help="Captchas Character Extractor")
@click.option("-i", help="captchas input path", default='tmp/generate')
@click.option("-o", help="captchas character output path", default='tmp/extract')
@click.option("-n", help="processed captchas count", default=10000)
def start_extract(i, o, n):
    extract(generate_dir=i, extract_dir=o, total=n)


@cli.command(help="Captchas Trainer")
@click.option("-i", help="captchas character input path", default='tmp/extract')
@click.option("-l", help="label output path", default='tmp/label.dat')
@click.option("-m", help="model output path", default='tmp/model.hdf5')
def start_train(i, l, m):
    train(extract_dir=i, label_file=l, model_file=m)


@cli.command(help="Captchas Predictor")
@click.option("-i", help="raw capcthas input path")
@click.option("-l", help="label input path", default='tmp/label.dat')
@click.option("-m", help="model input path", default='tmp/model.hdf5')
@click.option("-o", help="predicted captcha output path", default='tmp/predict')
@click.option("-c", help="captchas code length", default=4)
def start_predict(i, l, m, o, c):
    if not os.path.exists(i):
        return
    images = list(paths.list_images(i))
    predict(images=images, label_file=l, model_file=m, predict_dir=o, code_length=4)


if __name__ == "__main__":
    cli()
