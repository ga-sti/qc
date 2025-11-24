import argparse
from .gui import main as gui_main
from .collect import main as collect_main
from .merge import main as merge_main
from .excel import main as excel_main
from .report import main as report_main
from .pipeline import main as pipeline_main

def build_parser():
    p = argparse.ArgumentParser(description="QC Tool Runners (adapters)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("gui")
    sub.add_parser("collect")
    m = sub.add_parser("merge")
    m.add_argument("form_json")
    m.add_argument("system_json")
    e = sub.add_parser("excel")
    e.add_argument("record_json")
    r = sub.add_parser("report")
    r.add_argument("record_json")
    sub.add_parser("run")  # pipeline

    return p

def main(argv=None):
    p = build_parser()
    args = p.parse_args(argv)
    if args.cmd == "gui":
        gui_main()
    elif args.cmd == "collect":
        collect_main()
    elif args.cmd == "merge":
        merge_main(args.form_json, args.system_json)
    elif args.cmd == "excel":
        excel_main(args.record_json)
    elif args.cmd == "report":
        report_main(args.record_json)
    elif args.cmd == "run":
        pipeline_main()

if __name__ == "__main__":
    main()
