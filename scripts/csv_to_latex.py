import os
import argparse
import pandas as pd
import numpy as np

from datetime import datetime

def get_parser_csv_to_latex():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out_dir",
        default=None,                    
    )
    parser.add_argument(
        "--input_topics_filepath",
        type=str,
        default="reports/20240426_Tikz_sandbox/lst_topics.csv",
    )
    parser.add_argument(
        "--input_examples_filepath",
        type=str,
        default="reports/20240426_Tikz_sandbox/lst_ex.csv",
    )
    parser.add_argument(

        "--input_references_filepath",
        type=str,
        default="reports/20240426_Tikz_sandbox/lst_ref.csv",
    )
    parser.add_argument(
        "--pivot_index_columns",
        default="expression",
        help="pivotのindex(縦軸)に持ってくる列名(のリスト)"
    )
    parser.add_argument(
        "--pivot_columns",
        default="animename",
        help="pivotの列方向に持ってくる値を格納している列(のリスト)"
    )
    parser.add_argument(
        "--value_format_str",
        default="",
    )
    parser.add_argument(
        "--index_type",
        choices=["label", "int"],
        help="index(縦軸)のデータの形式。label:離散ラベル,int:整数,year_month:年月(YYMM)",
        default="label",
    )
    parser.add_argument(
        "--output_type",
        choices=["tikz", "tikz_tex", "table"],
    )
    parser.add_argument(
        "--tex_template_prefix_filepath",
        type=str,
        default="",
        help="tex先頭(prefix)テンプレートのファイルパス"
    )
    parser.add_argument(
        "--tex_template_postfix_filepath",
        type=str,
        default="",
        help="tex接尾辞(postfix)テンプレートのファイルパス"
    )
    parser.add_argument(
        "--draw_tikz_parent_relationship",
        help="親関係を描画する。tikzのみサポート",
        dest="is_draw_tikz_parent_relationship",
        action="store_true",
    )
    return parser

class RunCsvToLatex():
    def __init__(self, args_dict):
        self.args_dict = args_dict
        self.out_dir = self.args_dict["out_dir"]
        
        if self.out_dir is None:
            self.out_dir = os.path.join(
                "out",
                self.__class__.__name__,
                datetime.now().strftime("%Y%m%d%H%M%S")
            )
        os.makedirs(self.out_dir, exist_ok=True)
        self.is_draw_tikz_parent_relationship = self.args_dict["is_draw_tikz_parent_relationship"]
        if self.is_draw_tikz_parent_relationship:
            assert self.args_dict["output_type"] in ["tikz", "tikz_tex"], f"--is_draw_tikz_parent_relationship is supported for tikz output_type, but not for {self.args_dict['output_type']}."
        self.example_type_lst = [
            "Declaration",
            "Expression",
        ]
        self.tex_header = r"""\documentclass[dvipdfmx,a4paper]{jsarticle}% ドライバ dvipdfmx を指定する
\usepackage[svgnames]{xcolor}% tikzより前に読み込む必要あり
\usepackage{tikz}
\usepackage{url}
\usepackage{amsmath}
\usepackage{booktabs,longtable}

\begin{document}"""
#         self.footer = r"""\bibliographystyle{abbrv}
# \bibliography{reference}

# \end{document}
# """
        self.tex_footer = r"""
\end{document}
"""
        pass

    def run(self):
        df_example = pd.read_csv(self.args_dict["input_examples_filepath"])
        df_reference = pd.read_csv(self.args_dict["input_references_filepath"])
        df_topic = pd.read_csv(self.args_dict["input_topics_filepath"])
        df_ex_ref = pd.merge(df_example, df_reference, how="left", on="reference_id")
        df_ex_ref_topic = pd.merge(df_ex_ref, df_topic, how="left", on="topic_id")
        f = open(
            os.path.join(self.out_dir, "out.tex"),
            "w"
        )
        f.write(self.tex_header)

        for name, group in df_ex_ref_topic.groupby("topic_id"):
            # なかった時の対処？
            # TODO: exampleのないtopicは列挙されない。
            topic_dict = df_topic[df_topic["topic_id"] == name].iloc[0].to_dict()
            topic_title = topic_dict["topic_title"]
            # topic_name = df_topic[df_topic["topic_id"] == name]["topic_title"].values[0]
            f.write(f"\\section{{{topic_title}}}\n")
            print(f"{topic_title=}")

            columns_to_show_in_topic_table = ["example_type", "example_word", "reference_title", "page_or_section", "example_description_ja"]
            print(group[columns_to_show_in_topic_table].to_latex())
            f.write(group[columns_to_show_in_topic_table].rename(columns=lambda a: a.replace("_", "\_")).to_latex())
            for example_type in self.example_type_lst:
                print(f"{example_type=}")
                df_example_per_type = group[group["example_type"]==example_type]
                # ここで出すか、example_type絞らずに出すか。
                # df_example_per_type[["example_word", "reference_title", "page_or_section", "example_description_ja"]].to_latex()
                if df_example_per_type.empty:
                    print("Empty")
                    continue
                f.write(f"\\subsection{{{example_type} of {topic_title}}}\n")
                for ridx, row in df_example_per_type.iterrows():
                    f.write(f"\\paragraph{{{row["example_word"]}}}\n")
                    f.write(f"""
reference from {row['reference_id']}.
excerpts: {row['excerpts']},
translation: {row['translation']},
"""
                    )
                    pass

            pass
        pass
        f.write(self.tex_footer)
        f.close()


if __name__ == "__main__":
    engine = RunCsvToLatex(vars(get_parser_csv_to_latex().parse_args()))
    engine.run()