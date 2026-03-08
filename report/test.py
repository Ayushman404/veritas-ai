import pandas as pd
import textwrap

df = pd.read_csv("evaluation_report.csv")

def pretty_print_row(row):
    print("=" * 80)
    print(f"Query: {row['user_input']}\n")

    print("Model Answer:")
    print(textwrap.fill(row["response"], width=90))
    print()

    print("Ground Truth:")
    print(textwrap.fill(row["reference"], width=90))
    print()

    print("Metrics")
    print(f"Faithfulness      : {row['faithfulness']:.3f}")
    print(f"Answer Relevancy  : {row['answer_relevancy']:.3f}")
    print(f"Context Precision : {row['context_precision']:.3f}")
    print("=" * 80)
    print()

for _, row in df.iterrows():
    pretty_print_row(row)