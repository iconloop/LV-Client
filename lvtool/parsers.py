import argparse

from .types import Commands


def init_parsers():
    parser = argparse.ArgumentParser(prog="LV Tool")
    subparsers = parser.add_subparsers(dest="dest")

    vpr_request(subparsers.add_parser(Commands.VPR, help=vpr_request.__doc__))
    vid_request(subparsers.add_parser(Commands.VID, help=vid_request.__doc__))
    auth_token(subparsers.add_parser(Commands.TOKEN, help=auth_token.__doc__))
    write_clues(subparsers.add_parser(Commands.STORE, help=write_clues.__doc__))
    read_clues(subparsers.add_parser(Commands.RESTORE, help=read_clues.__doc__))
    make_vp(subparsers.add_parser(Commands.MAKEVP, help=make_vp.__doc__))

    return parser


def vpr_request(parser):
    """Request VPR."""
    parser.add_argument("-d", "--debug", action='store_true', help="Run lv-tool in debug mode. (More log output)")
    parser.add_argument("-e", "--endpoint", required=True, help="Endpoint of LV Manager.")
    parser.add_argument("-o", "--output", required=True, help="Output path of results after VPR request.")


def vid_request(parser):
    """Request VID and Storages with VP."""
    parser.add_argument("-d", "--debug", action='store_true', help="Run lv-tool in debug mode. (More log output)")
    parser.add_argument("-e", "--endpoint", required=True, help="Endpoint of LV Manager.")
    parser.add_argument("-f", "--input", required=True, help="VPR")
    parser.add_argument("-v", "--vp", help="VP")
    parser.add_argument("-o",
                        "--output",
                        required=True,
                        help="Output path of results after VP authentication finished.")


def auth_token(parser):
    """Request token to Storages."""
    parser.add_argument("-d", "--debug", action='store_true', help="Run lv-tool in debug mode. (More log output)")
    parser.add_argument("-f", "--input", required=True, help="VID RESPONSE message which contains info of storages.")
    parser.add_argument("-o", "--output", required=True, help="Token output after Storage authentication finished.")


def write_clues(parser):
    """Write clue to given storages."""
    # parser.add_argument("clues", nargs="+", help="Clues to be stored")
    parser.add_argument("-d", "--debug", action='store_true', help="Run lv-tool in debug mode. (More log output)")
    parser.add_argument("clues", help="Clue file to be stored")
    parser.add_argument("-f", "--input", required=True, help="Storage info with token.")
    parser.add_argument("-o", "--output", required=True, help="Stored info output after clues are stored.")


def read_clues(parser):
    """Request clue by given vid."""
    parser.add_argument("-d", "--debug", action='store_true', help="Run lv-tool in debug mode. (More log output)")
    parser.add_argument("-f", "--input", required=True, help="Storage info with clue vid and tag.")
    parser.add_argument("-o", "--output", required=True, help="Output path of requested clues.")


def make_vp(parser):
    """Make a VP with the given UserID and PIN."""
    parser.add_argument("-d", "--debug", action='store_true', help="Run lv-tool in debug mode. (More log output)")
    parser.add_argument("-u", "--userid", required=True, help="User ID for VP")
    parser.add_argument("-p", "--pin", required=True, help="Pin for VP")
