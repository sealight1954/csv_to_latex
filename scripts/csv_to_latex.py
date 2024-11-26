import os
import argparse
import pandas as pd
import numpy as np
import json
import enum

from datetime import datetime

class DataFrameColumnNames(enum.Enum):
    topic_number=0,
    topic_id=enum.auto(),
    topic_title=enum.auto(),
    topic_category=enum.auto(),
    topic_list_of_words=enum.auto(),
    topic_description_ja=enum.auto(),
    topic_description_en=enum.auto(),
    topic_notes=enum.auto(),
    topic_registerer_name=enum.auto(),
    topic_registered_date=enum.auto(),
    topic_updated_date=enum.auto(),
    # notes_private=enum.auto()
    # Reference
    reference_number=enum.auto(),
    reference_id=enum.auto(),
    reference_title=enum.auto(),
    reference_author=enum.auto(),
    reference_organization=enum.auto(),
    reference_type=enum.auto(),
    reference_description_ja=enum.auto(),
    reference_description_en=enum.auto(),
    reference_year=enum.auto(),
    reference_date=enum.auto(),
    reference_publication_type=enum.auto(),
    reference_citation=enum.auto(),
    reference_notes=enum.auto()
    # Example
    example_number=enum.auto(),
    # topic_id, ExampleからTopicを参照
    # reference_id, ExampleからReferenceを参照
    example_type=enum.auto(),
    example_word=enum.auto(),
    example_page_or_section=enum.auto(),
    example_excerpts=enum.auto(),
    example_translation=enum.auto(),
    example_description_ja=enum.auto(),
    example_description_en=enum.auto(),
    example_notes=enum.auto()




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
        "--column_name_dict_json_str_preferred",
        default=None,
        type=str
    )
    parser.add_argument(
        "--reference_id_column_name",
        default="reference_id",
        type=str,
    )
    parser.add_argument(
        "--reference_title_column_name",
        default="reference_title",
        type=str,
    )
    parser.add_argument(
        "--topic_id_column_name",
        default="topic_id",
        type=str,
    )
    parser.add_argument(
        "--topic_title_column_name",
        default="topic_title",
        type=str,
    )
    parser.add_argument(
        "--example_type_column_name",
        default="example_type",
        type=str,
    )
    parser.add_argument(
        "--example_word_column_name",
        default="example_word",
        type=str,
    )
    parser.add_argument(
        "--excerpt_column_name",
        default="excerpt",
        type=str,
    )
    parser.add_argument(
        "--translation_column_name",
        default="translation",
        type=str,
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
    return parser

def generate_table(data_frame, columns_to_show=None, table_title="") -> str:
    if columns_to_show is not None:
        data_frame = data_frame[columns_to_show]
    table_str = f"""\\begin{{table}}[hbp]
\\caption{{{table_title}}}
{data_frame.rename(columns=lambda a: a.replace("_", "-")).to_latex().replace("lllll", "lC{2cm}C{3cm}C{2cm}C{3cm}")}
\\end{{table}}
"""
    return table_str

def generate_bib_misc(bib_id="", author="", url="", title="", year="", organization="") -> str:
    bib_str = f"""
@Misc{{{bib_id},
  author       = {{{author}}},
  howpublished = {{\\url{{{url}}}}},
  title        = {{{title}}},
  year         = {{{year}}},
  institution  = {{{organization}}}
}}
"""
    return bib_str

def generate_reference_bib(data_frame: pd.DataFrame) -> str:
    # f = open(out_filepath, "w")
    bib_str = ""
    for ridx, row in data_frame.iterrows():
        bib_dict = dict(
            bib_id=row[DataFrameColumnNames.reference_id.name],
            author=row[DataFrameColumnNames.reference_author.name],
            url=row[DataFrameColumnNames.reference_notes.name],
            title=row[DataFrameColumnNames.reference_title.name],
            year=row[DataFrameColumnNames.reference_year.name],
            organization=row[DataFrameColumnNames.reference_organization.name],
        )
        misc_str = generate_bib_misc(**bib_dict)
        bib_str += misc_str
        pass
    return bib_str
    


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
        self.example_type_lst = [
            "Declaration",
            "Expression",
        ]
        self.tex_header = r"""\documentclass[dvipdfmx,a4paper]{article}% ドライバ dvipdfmx を指定する
\usepackage[svgnames]{xcolor}% tikzより前に読み込む必要あり
\usepackage{tikz}
\usepackage{url}
\usepackage{amsmath}
\usepackage{booktabs,longtable}
% https://tex.stackexchange.com/questions/286950/how-to-create-a-table-with-fixed-column-widths
\usepackage{array}
\newcommand{\PreserveBackslash}[1]{\let\temp=\\#1\let\\=\temp}
\newcolumntype{C}[1]{>{\PreserveBackslash\centering}p{#1}}
\newcolumntype{R}[1]{>{\PreserveBackslash\raggedleft}p{#1}}
\newcolumntype{L}[1]{>{\PreserveBackslash\raggedright}p{#1}}

\title{List of Examples}
\author{author name}
\begin{document}

\maketitle
\tableofcontents

\clearpage
"""
        self.tex_footer = r"""\bibliographystyle{abbrv}
\bibliography{reference}
\listoftables

\end{document}
"""
        if self.args_dict["column_name_dict_json_str_preferred"] is not None:
            self.colum_name_dict = json.loads(self.args_dict["column_name_dict_json_str_preferred"])
        else:
            self.colum_name_dict = dict(
                reference_id=self.args_dict["reference_id_column_name"],
                reference_title=self.args_dict["reference_title_column_name"],
                topic_id=self.args_dict["topic_id_column_name"],
                topic_title=self.args_dict["topic_title_column_name"],
                example_type=self.args_dict["example_type_column_name"],
                example_word=self.args_dict["example_word_column_name"],
                excerpt=self.args_dict["excerpt_column_name"],
                translation=self.args_dict["translation_column_name"],
            )

    def run(self):
        df_example = pd.read_csv(self.args_dict["input_examples_filepath"])
        df_reference = pd.read_csv(self.args_dict["input_references_filepath"])
        # df_reference["reference_title_with_citation"] = df_reference.apply(lambda x: f"{x[DataFrameColumnNames.reference_title.name]}\\cite{{{x[DataFrameColumnNames.reference_id.name]}}}", axis=1)
        bib_str = generate_reference_bib(df_reference)
        with open(os.path.join(
            self.out_dir, "reference.bib"
        ), "w") as f:
            f.write(bib_str)
        df_topic = pd.read_csv(self.args_dict["input_topics_filepath"])
        df_ex_ref = pd.merge(df_example, df_reference, how="left", on=DataFrameColumnNames.reference_id.name)
        df_ex_ref_topic = pd.merge(df_ex_ref, df_topic, how="left", on=DataFrameColumnNames.topic_id.name)
        df_ex_ref_topic["reference_title_with_citation"] = df_ex_ref_topic.apply(lambda x: f"{x[DataFrameColumnNames.reference_title.name]}\\cite{{{x[DataFrameColumnNames.reference_id.name]}}}", axis=1)
        df_ex_ref_topic["reference_details"] = df_ex_ref_topic.apply(lambda x: f"{x[DataFrameColumnNames.example_page_or_section.name]} of {x[DataFrameColumnNames.reference_title.name]}\\cite{{{x[DataFrameColumnNames.reference_id.name]}}}", axis=1)


        f = open(
            os.path.join(self.out_dir, "out.tex"),
            "w"
        )
        f.write(self.tex_header)

        for name, group in df_ex_ref_topic.groupby(DataFrameColumnNames.topic_id.name):
            # なかった時の対処？
            # TODO: exampleのないtopicは列挙されない。
            topic_dict = df_topic[df_topic[DataFrameColumnNames.topic_id.name] == name].iloc[0].to_dict()
            topic_title = topic_dict[DataFrameColumnNames.topic_title.name]
            # topic_name = df_topic[df_topic[DataFrameColumnNames.topic_id.name] == name][DataFrameColumnNames.topic_title.name].values[0]
            f.write(f"\\section{{{topic_title}}}\n")
            # f.write(f"\\section{{{topic_title} from {topic_dict[DataFrameColumnNames.reference_title.name]}\\citation{{{topic_dict[DataFrameColumnNames.reference_id.name]}}}}}\n")
            print(f"{topic_title=}")
            f.write(f"""
\\paragraph{{Topic Title}} Topic-No.{topic_dict[DataFrameColumnNames.topic_number.name]} {topic_dict[DataFrameColumnNames.topic_title.name]}
\\paragraph{{List of Words}} {topic_dict[DataFrameColumnNames.topic_list_of_words.name]}
\\paragraph{{Category}} {topic_dict[DataFrameColumnNames.topic_category.name]}
\\paragraph{{Description}} {topic_dict[DataFrameColumnNames.topic_description_ja.name]}\\\\{topic_dict[DataFrameColumnNames.topic_description_en.name]}
\\paragraph{{Registerer Name}} {topic_dict[DataFrameColumnNames.topic_registerer_name.name]}
\\paragraph{{Notes}} {topic_dict[DataFrameColumnNames.topic_notes.name]}
"""
            )


            columns_to_show_in_topic_table = [DataFrameColumnNames.example_type.name, DataFrameColumnNames.example_word.name, "reference_details", DataFrameColumnNames.example_description_ja.name]
            print(group[columns_to_show_in_topic_table].to_latex())

            f.write(generate_table(data_frame=group, columns_to_show=columns_to_show_in_topic_table, table_title=f"Example list of \"{topic_title}\""))
            # f.write(group[columns_to_show_in_topic_table].rename(columns=lambda a: a.replace("_", "\_")).to_latex())
            for example_type in self.example_type_lst:
                print(f"{example_type=}")
                df_example_per_type = group[group[DataFrameColumnNames.example_type.name]==example_type]
                # ここで出すか、example_type絞らずに出すか。
                # df_example_per_type[["example_word", "reference_title", "page_or_section", "example_description_ja"]].to_latex()
                if df_example_per_type.empty:
                    print("Empty")
                    continue
                f.write(f"\\subsection{{{example_type} list of {topic_title}}}\n")
                for ridx, row in df_example_per_type.iterrows():
                    f.write(f"\\subsubsection{{{row[DataFrameColumnNames.example_word.name]} from {row[DataFrameColumnNames.example_page_or_section.name]} of {row[DataFrameColumnNames.reference_title.name]}\\cite{{{row[DataFrameColumnNames.reference_id.name]}}}}}\n")
                    # f.write(f"\\subsubsection{{{row[DataFrameColumnNames.example_word.name]}}}\n")
                    f.write(f"""
\\paragraph{{Example Word}} No.{row[DataFrameColumnNames.example_number.name]} {row[DataFrameColumnNames.example_word.name]}
\\paragraph{{Reference}} Reference from {row['reference_title_with_citation']} {row[DataFrameColumnNames.example_page_or_section.name]}.
\\paragraph{{Excerpts}} {row[DataFrameColumnNames.example_excerpts.name]}
\\paragraph{{Translation}} {row[DataFrameColumnNames.example_translation.name]}
\\paragraph{{Description}} {row[DataFrameColumnNames.example_description_ja.name]}\\\\{row[DataFrameColumnNames.example_description_en.name]}
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