# How to Use the Gemini Planning Prompt

This guide explains how to use the Gemini prompt to create a comprehensive planning document for your quantitative trading project.

## Step 1: Access Gemini

Go to [Google Gemini](https://gemini.google.com/) or use Gemini in your preferred interface.

## Step 2: Copy the Prompt

Open the file `gemini_planning_prompt.txt` and copy the entire contents.

```bash
cat gemini_planning_prompt.txt | pbcopy  # macOS
cat gemini_planning_prompt.txt | xclip   # Linux
```

Or simply open it and copy manually:
```bash
open gemini_planning_prompt.txt  # macOS
```

## Step 3: Submit to Gemini

1. Paste the entire prompt into Gemini's chat interface
2. Send the message
3. Wait for Gemini to generate the comprehensive planning document

## Step 4: Review and Customize

1. Gemini will generate a detailed planning document
2. Copy the output
3. Save it as `PROJECT_PLAN.md` in your project root:
   ```bash
   # Create the file and paste Gemini's output
   nano PROJECT_PLAN.md
   ```

## Step 5: Refine with Follow-ups

You can ask Gemini follow-up questions to refine specific sections:

**Example follow-ups:**
- "Can you expand on the machine learning integration section with specific algorithms and implementation steps?"
- "What are the top 5 most important tasks I should start with this week?"
- "Can you provide more detail on implementing walk-forward analysis?"
- "What testing framework structure would you recommend for this project?"
- "Can you create a detailed 30-day sprint plan based on this roadmap?"

## Step 6: Track Progress

Use the template structure provided in `PLANNING_TEMPLATE.md` or the output from Gemini to:

1. Create issues in GitHub
2. Set up a project board
3. Track milestones
4. Update the plan regularly

## Alternative: Use Gemini API

If you want to automate this, you can use the Gemini API:

```python
import google.generativeai as genai

# Configure API
genai.configure(api_key='YOUR_API_KEY')
model = genai.GenerativeModel('gemini-pro')

# Read prompt
with open('gemini_planning_prompt.txt', 'r') as f:
    prompt = f.read()

# Generate planning document
response = model.generate_content(prompt)
planning_doc = response.text

# Save to file
with open('PROJECT_PLAN.md', 'w') as f:
    f.write(planning_doc)

print("Planning document created: PROJECT_PLAN.md")
```

## Tips for Best Results

1. **Be Specific**: If Gemini's output is too generic, ask for more specific, actionable items
2. **Iterate**: Use follow-up prompts to dive deeper into specific areas
3. **Contextualize**: Add information about your specific goals, timeline, or constraints
4. **Validate**: Review technical recommendations and adjust based on your expertise
5. **Keep Updated**: Regenerate or update sections as your project evolves

## Example Customization Prompts

**For your specific situation:**
```
"I have 2 hours per day to work on this project. Can you adjust the roadmap
timeline accordingly and prioritize the most impactful tasks?"
```

```
"I'm particularly interested in machine learning strategies. Can you create
a detailed 90-day plan focused on implementing ML-based alpha strategies?"
```

```
"I want to focus on factor investing. Can you expand the strategy development
section with specific factor models to implement (value, momentum, quality, etc.)?"
```

```
"Can you create a testing strategy with specific test cases for each module
in the project?"
```

## What to Do with the Output

1. **Save**: Store as `PROJECT_PLAN.md` in your repo
2. **Version Control**: Commit to git
3. **Review Weekly**: Update progress and adjust priorities
4. **Share**: Use for collaboration or documentation
5. **Create Issues**: Convert tasks into GitHub issues
6. **Track**: Use GitHub Projects or other tools to manage tasks

## Need Help?

If Gemini's output doesn't meet your needs:
- Try rephrasing the prompt
- Add more context about your specific goals
- Ask for examples or code snippets
- Request specific formats (tables, checklists, code blocks)

---

**Pro Tip**: Save Gemini's responses with timestamps so you can track how your planning evolves over time.
