import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the Excel file
file_path = 'graded_output1.xlsx'
data = pd.read_excel(file_path)

# Extract the 'better_answer' column and grade columns
better_answer = data['better_answer']
my_grade = data['my_grade']
gpt_grade = data['gpt_grade']

# Count the occurrences of 'My Answer' and 'Answer 2'
answer_counts = better_answer.value_counts()

# Create the figure with subplots (1 row, 2 columns)
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Bar chart (Better Answer for Beginners)
axes[0].bar(answer_counts.index, answer_counts.values, color=['lightblue', 'lightcoral'])
axes[0].set_title('Better Answer for Beginners: My Answer vs GPT Answer', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Answer', fontsize=12)
axes[0].set_ylabel('Count', fontsize=12)

# Boxplot (Grades comparison)
axes[1].boxplot([my_grade, gpt_grade], vert=False, labels=['My Grade', 'GPT Grade'], patch_artist=True, 
                showfliers=True, medianprops={'color': 'black', 'linewidth': 2}, 
                whiskerprops={'linewidth': 1.5}, capprops={'linewidth': 1.5})

# Customize the boxplot
axes[1].set_title('Box and Whiskers Plot of My Grade vs GPT Grade', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Grades', fontsize=12)

# Display the plot
plt.tight_layout()
plt.show()
