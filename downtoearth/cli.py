#!/usr/bin/env python
"""downtoearth creates terraform files from api configuration definitions."""
import argparse

from downtoearth.model import ApiModel


def parse_args():
    """Parse arguments."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='command')
    generate_parser = subparsers.add_parser(
        'generate',
        help='generate a terraform API file'
    )
    generate_parser.add_argument(
        '-c',
        '--composable',
        action='store_true',
        help='Modify output to permit combining with other terraform configurations'
    )
    generate_parser.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help="Don't echo the terraform"
    )
    generate_parser.add_argument('input', help="dte.json configuration file")
    generate_parser.add_argument('output', help="destination for .tf file")
    generate_parser.set_defaults(execute_step=generate)
    deploy_parser = subparsers.add_parser(
        'deploy',
        help='publishes a new lambda versiona and then points an alias to that version based on the stage name'
    )
    deploy_parser.add_argument('input', help="dte.json configuration file")
    deploy_parser.add_argument('stage', help="stage to deploy lambda to")
    deploy_parser.set_defaults(execute_step=deploy)
    tf_parser = subparsers.add_parser(
        'tf',
        help='apply/plan terraform changes'
    )
    tf_parser.add_argument(
        '-c',
        '--composable',
        action='store_true',
        help='Modify output to permit combining with other terraform configurations'
    )
    tf_parser.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help="Don't echo the terraform"
    )
    tf_parser.add_argument(
        '-v',
        '--var',
        default='terraform.tfvars',
        help="name of varfile"
    )
    tf_parser.add_argument('input', help="dte.json configuration file")
    tf_parser.add_argument('output', help="destination for .tf file")
    tf_parser.set_defaults(execute_step=terraform_run)
    tfvar_parser = subparsers.add_parser(
        'tfvar',
        help='create tfvar file with lambda aliases'
    )
    tfvar_parser.add_argument('input', help="dte.json configuration file")
    tfvar_parser.add_argument('output', help="destination for .tfvar file")
    tfvar_parser.set_defaults(execute_step=terraform_var)
    args = parser.parse_args()
    return args


def generate(args, model=None):
    model = model if model is not None else ApiModel(args)
    output = model.render_terraform()
    with open(args.output, "w") as f:
        f.write(output)
    if not args.quiet:
        print(output)


def deploy(args):
    model = ApiModel(args)
    model.run_stage_deployment(args.stage)


def terraform_var(args):
    model = ApiModel(args)
    model.get_lambda_versions_file(args.output)


def terraform_run(args):
    model = ApiModel(args)
    generate(args, model)
    model.run_terraform(args.var)


def main():
    """Build template and output to file."""
    args = parse_args()
    if args.execute_step:
        args.execute_step(args)


if __name__ == "__main__":
    main()
