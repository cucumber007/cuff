from datetime import datetime
import json

#git log --abbrev-commit --shortstat --graph --date=short > log.txt


commits = []

with open("git.log", "r") as f:
	current_commit = None
	current_index = 0

	for index, line in enumerate(f.readlines()):
		#print(line[0])
		if line[0] == "*":
			if current_commit:
				commits.append(current_commit)
			current_commit = {
				"files_changed": 0,
				"insertions": 0,
				"deletions": 0,
			}
			current_index = index
			#print("*")
		else:
			if "Date:" in line:
				date = datetime.strptime(line.split("Date:")[-1].strip(), "%Y-%m-%d")
				current_commit["date"] = date
				#print(date)
			if "Author:" in line:
				author = line.split("<")[1].split(">")[0]
				current_commit["author"] = author
			if "files changed" in line:
				#5 files changed, 86 insertions(+), 11 deletions(-)
				line = line.replace("|", "")
				files_changed = line.split("files changed")[0].strip()
				if "insertions" in line:
					insertions = line.split(",")[1].split(" ")[1].strip()
				else:
					insertions = 0

				if "deletions" in line:
					deletions = line.split(",")[2].split(" ")[1].strip()
				else:
					deletions = 0

				current_commit["files_changed"] = int(files_changed)
				current_commit["insertions"] = int(insertions)
				current_commit["deletions"] = int(deletions)
	#print(json.dumps(commits, indent=4))

stats = {}
sum_changes = 0
sum_norm = 0

for index, commit in enumerate(commits):
	author = commit["author"]
	date = commit["date"]
	if author not in stats:
		stats[author] = {}
	if date not in stats[author]:
		stats[author][date] = {
			"files_changed": 0,
			"lines_changed": 0,
			"insertions": 0,
			"deletions": 0,
			"normalized_changes": 0,
			"avg_changes": 0,
			"avg_normalized_changes": 0,
		}
	stats[author][date]["files_changed"] += commit["files_changed"]
	stats[author][date]["lines_changed"] += commit["insertions"] + commit["deletions"]
	stats[author][date]["insertions"] += commit["insertions"]
	stats[author][date]["deletions"] += commit["deletions"]
	stats[author][date]["normalized_changes"] += round(stats[author][date]["lines_changed"] / (commit["files_changed"]+1))
	sum_changes += stats[author][date]["lines_changed"]
	sum_norm += stats[author][date]["normalized_changes"]
	num_days = len(stats[author].keys())
	stats[author][date]["avg_changes"] = round(sum_changes / num_days)
	stats[author][date]["avg_normalized_changes"] = round(sum_norm / num_days)

with open("res.csv", "w") as r:
	title_printed = False
	for author in sorted(stats.keys()):
		for date in sorted(stats[author].keys()):
			if not title_printed:
				keys = stats[author][date].keys()
				r.write(("author,date"+(",{}"*len(keys))+"\n").format(*keys))
				title_printed = True
			res = (",{}"*(len(keys)+2)+"\n")[1:].format(
					author,
					date, 
					*map(lambda x: stats[author][date][x], stats[author][date].keys())
				)
			#print(res)
			r.write(res)