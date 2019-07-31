from datetime import datetime
import json
import matplotlib.pyplot as plt

#git log --abbrev-commit --shortstat --graph --date=short > log.txt


commits = []

with open("git.log", "r") as f:
	current_commit = None
	current_index = 0

	for index, line in enumerate(f.readlines()):
		#print(line[0])
		if "*" in line[0]:
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
			"normalized_changes": 0
		}
	stats[author][date]["files_changed"] += commit["files_changed"]
	stats[author][date]["lines_changed"] += commit["insertions"] + commit["deletions"]
	stats[author][date]["insertions"] += commit["insertions"]
	stats[author][date]["deletions"] += commit["deletions"]
	stats[author][date]["normalized_changes"] = round(stats[author][date]["lines_changed"] / (commit["files_changed"]+1)) * 25
	#print(stats[author][date]["normalized_changes"])

for author in stats.keys():
	sum_lines = 0
	sum_norm = 0
	
	for date_index, date in enumerate(sorted(stats[author].keys())):
		if "avg_lines" not in stats[author][date]:
			stats[author][date]["avg_lines"] = 0
		if "avg_norm" not in stats[author][date]:
			stats[author][date]["avg_norm"] = 0
		sum_lines += stats[author][date]["lines_changed"]
		sum_norm += stats[author][date]["normalized_changes"]
		stats[author][date]["avg_norm"] = sum_norm / (date_index+1)
		stats[author][date]["avg_lines"] = sum_lines / (date_index+1)
		#print(sum_norm, (date_index+1), sum_norm / (date_index+1), stats[author][date]["normalized_changes"])

for author in sorted(stats.keys()):
	dates = sorted(list(stats[author].keys()))
	plt.bar(dates, list(map(lambda x: stats[author][x]["lines_changed"], dates)))
	plt.plot(dates, list(map(lambda x: stats[author][x]["avg_lines"], dates)), "r")
	plt.plot(dates, list(map(lambda x: stats[author][x]["avg_norm"], dates)), "g")
	#plt.bar(dates, list(map(lambda x: stats[author][x]["normalized_changes"], dates)))
	#plt.ylabel('some numbers')
	plt.xlabel('dates')
	plt.show()


with open("res.csv", "w") as r:
	title_printed = False
	for author in sorted(stats.keys()):
		for date in sorted(stats[author].keys()):
			if not title_printed:
				keys = stats[author][date].keys()
				r.write(("author,date"+(",\t{}"*len(keys))+"\n").format(*keys))
				title_printed = True
			res = (",{}\t"*(len(keys)+2)+"\n")[1:].format(
					author.split("@")[0],
					date.strftime("%d-%m-%y"), 
					*map(lambda x: round(stats[author][date][x]), stats[author][date].keys())
				)
			#print(res)
			r.write(res)