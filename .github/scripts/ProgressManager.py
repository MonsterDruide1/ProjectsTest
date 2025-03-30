from github import Github, Auth
from enum import Enum
import ryml
import cxxfilt
import os, requests

DRY_RUN = False
OWNER = "MonsterDruide1"
REPO = "ProjectsTest"
FINE_TOKEN = os.getenv("FINE_TOKEN")
PROJECT_TOKEN = os.getenv("PROJECT_TOKEN")

PROJECT_ID = "PVT_kwHOAZIPJM4AxQt0"
STATUS_ID = "PVTSSF_lAHOAZIPJM4AxQt0zgnZrEM"
STATUS_TODO_ID = "f75ad846"
STATUS_INPROGRESS_ID = "47fc9ee4"
STATUS_DONE_ID = "98236657"

class FunctionStatus(Enum):
    Matching = 0
    NonMatchingMinor = 1
    NonMatchingMajor = 2
    NotDecompiled = 3
    Wip = 4
    Library = 5

def char_to_status(char: str) -> FunctionStatus:
    if char == 'O':
        return FunctionStatus.Matching
    elif char == 'm':
        return FunctionStatus.NonMatchingMinor
    elif char == 'M':
        return FunctionStatus.NonMatchingMajor
    elif char == 'U':
        return FunctionStatus.NotDecompiled
    elif char == 'W':
        return FunctionStatus.Wip
    elif char == 'L':
        return FunctionStatus.Library
    else:
        raise ValueError(f"Unknown status character: {char}")

class Function:
    def __init__(self, offset: int, status: FunctionStatus, size: int, name: str, lazy: bool):
        self.offset = offset
        self.status = status
        self.size = size
        self.name = name
        self.lazy = lazy
    
    def get_issue_line(self):
        try:
            demangled_name = cxxfilt.demangle(self.name)
        except Exception as e:
            print(f"Failed to demangle {self.name}: {e}")
            demangled_name = self.name + " (demangle failed)"
        return f"| " +\
               f"{'⬜' if self.status == FunctionStatus.NotDecompiled else '✅'}" +\
               f" | `0x{self.offset:08X}` | `{demangled_name}`{' (lazy)' if self.lazy else ''} | {self.size}" +\
               f" |"

class File:
    # functions: dict[offset: int, tuple[status: FunctionStatus, size: int, mangled: str]]
    def __init__(self, functions: list[Function]):
        self.functions = functions
    
    def is_implemented(self):
        return all(f.status != FunctionStatus.NotDecompiled for f in self.functions)
    
    def issue_body(self):
        body = f"""\
The following functions should be listed in this class:
| status | address | function | size (bytes) |
| :----: | :------ | :------- | :----------- |
{"\n".join([f.get_issue_line() for f in self.functions])}
        """
        if len(body) > 65536:
            body = body[:65500]
            # delete until last newline
            body = body[:body.rfind("\n")]
            body += "\n... (truncated)"
        return body

print("Loading function CSV...")
# offset: (status, size, name)
function_csv = {}
with open('data/odyssey_functions.csv', 'r') as f:
    lines = f.readlines()[1:]
    for line in lines:
        offset, status, size, name = line.strip().split(',')
        function_csv[int(offset, 16)] = (char_to_status(status), int(size), name)

print("Loading file list...")
file_list = {}
with open('data/file_list.yml', 'r') as f:
    tree = ryml.parse_in_arena(bytes(f.read(), 'utf-8'))
    for file_id in ryml.children(tree, tree.root_id()):
        filename = tree.key(file_id).tobytes().decode()
        functions_data = tree.find_child(file_id, b".text")

        functions = []
        for function_id in ryml.children(tree, functions_data):
            # each line is another list itself
            if tree.num_children(function_id) != 1:
                raise ValueError(f"Unexpected number of children in file {filename}: {tree.num_children(function_id)}")
            function_nested_id = next(iter(ryml.children(tree, function_id)))

            offset = int(tree.key(function_nested_id).tobytes().decode(), 16)
            function = tree.val(function_nested_id).tobytes().decode()
            lazy = function.startswith("LAZY ")
            if lazy:
                function = function[5:]
            status, size, name = function_csv[offset]
            functions.append(Function(offset, status, size, name, lazy))
        file_list[filename] = File(functions)

# Limit to first 8 files for testing
#file_list = {k: file_list[k] for k in list(file_list)[:20]}

auth = Auth.Token(FINE_TOKEN)
g = Github(auth=auth)

repo = g.get_repo(OWNER+"/"+REPO)
label_unmanaged = repo.get_label("unmanaged")
label_implement = repo.get_label("implement")

print("Iterating and adjusting issues...")
files_handled = set()
for issue in repo.get_issues(state="open"):
    if label_unmanaged in issue.labels:
        continue

    if issue.title.startswith("Implement "):
        file_name = issue.title.split("Implement ")[1]
        if file_name not in file_list:
            print(f"Deleting issue: {issue.title}")
            if not DRY_RUN:
                issue.create_comment(body="File has been removed from the file list.")
                issue.edit(state="closed")
            continue
        file = file_list[file_name]
        if file.is_implemented():
            files_handled.add(file_name)
            print(f"Deleting issue: {issue.title}")
            if not DRY_RUN:
                issue.create_comment(body="File has been implemented.")
                issue.edit(state="closed")
            continue

        target_body = file_list[file_name].issue_body()
        if issue.body != target_body:
            print(f"Updating issue: {issue.title}")
            if not DRY_RUN:
                issue.edit(body=target_body)

        # issue is up to date!
        files_handled.add(file_name)
        continue

    # unknown issue, mark as unhandled/ignore
    print(f"Unknown issue: {issue.title}")
    if not DRY_RUN:
        issue.add_to_labels(label_unmanaged)

print("Checking for missing issues...")
for file_name, file in file_list.items():
    if file_name in files_handled:
        continue
    if file.is_implemented():
        continue
    print(f"Creating issue: Implement {file_name}")
    if not DRY_RUN:
        issue = repo.create_issue(
            title=f"Implement {file_name}",
            body=file.issue_body(),
            labels=[label_implement]
        )

print("Checking status of project...")

def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers={"Authorization": "Token " + PROJECT_TOKEN})
    if request.status_code == 200:
        response = request.json()
        if 'errors' in response:
            raise Exception("Query failed to run by returning error {}\nRequest: {}".format(response['errors'], query))
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

def get_project_items(project_id):
    return run_query("""
        {
            node(id: "PROJECT_ID") {
                ... on ProjectV2 {
                    items {
                        nodes {
                            id
                            title: fieldValueByName(name: "Title") {
                                ... on ProjectV2ItemFieldTextValue {
                                    text
                                }
                            }
                            status: fieldValueByName(name: "Status") {
                                ... on ProjectV2ItemFieldSingleSelectValue {
                                    field {
                                        ... on ProjectV2SingleSelectField {
                                            id
                                        }
                                    }
                                    name
                                }
                            }
                            content {
                                ...on Issue {
                                    number
                                    assignees {
                                        totalCount
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    """.replace("PROJECT_ID", project_id))

def get_issue_id(issue_number):
    return run_query("""
        {
            repository(owner: "OWNER", name: "REPO") {
                issue(number: ISSUE_ID) {
                    id
                }
            }
        }
    """.replace("OWNER", OWNER).replace("REPO", REPO).replace("ISSUE_ID", str(issue_number)))['data']['repository']['issue']['id']

def add_project_item(project_id, content_id):
    return run_query("""
        mutation {
            addProjectV2ItemById(input: {projectId: "PROJECT_ID", contentId: "CONTENT_ID"}) {
                item {
                    id
                }
            }
        }
    """.replace("PROJECT_ID", project_id).replace("CONTENT_ID", content_id))['data']['addProjectV2ItemById']['item']['id']

def delete_project_item(project_id, item_id):
    run_query("""
        mutation {
            deleteProjectV2Item(input: {projectId: "PROJECT_ID", itemId: "ITEM_ID"}) {
                deletedItemId
            }
        }
    """.replace("PROJECT_ID", project_id).replace("ITEM_ID", item_id))

def set_project_item_status(project_id, item_id, status_id, status_value_id):
    run_query("""
        mutation {
            updateProjectV2ItemFieldValue(input: {
                projectId: "PROJECT_ID",
                itemId: "ITEM_ID",
                fieldId: "STATUS_ID",
                value: {singleSelectOptionId: "DONE_ID"}
            }) {
                projectV2Item {
                    id
                }
            }
        }
    """.replace("PROJECT_ID", project_id).replace("ITEM_ID", item_id).replace("STATUS_ID", status_id).replace("DONE_ID", status_value_id))

# get project items

project_graphql = get_project_items(PROJECT_ID)
project_items = project_graphql['data']['node']['items']['nodes']

issues_handled = set()
for item in project_items:
    if item['status']['name'] == "Done":
        continue  # ignore done items

    title = item['title']['text']
    if title.startswith("Implement "):
        file_name = title.split("Implement ")[1]
        if file_name not in file_list:
            print(f"Deleting item: {title}")
            if not DRY_RUN:
                delete_project_item(PROJECT_ID, item['id'])
            continue
        file = file_list[file_name]
        if file.is_implemented():
            issues_handled.add(item['content']['number'])
            print(f"Moving item to Done: {title}")
            if not DRY_RUN:
                set_project_item_status(PROJECT_ID, item['id'], item['status']['field']['id'], STATUS_DONE_ID)
            continue

        if (item['status']['name'] == "In Progress") != (item['content'] is not None and item['content']['assignees']['totalCount'] > 0):
            if item['content'] is not None and item['content']['assignees']['totalCount'] > 0:
                print(f"Moving item to In Progress: {title}")
                if not DRY_RUN:
                    set_project_item_status(PROJECT_ID, item['id'], item['status']['field']['id'], STATUS_INPROGRESS_ID)
            else:
                print(f"Moving item to Todo: {title}")
                if not DRY_RUN:
                    set_project_item_status(PROJECT_ID, item['id'], item['status']['field']['id'], STATUS_TODO_ID)

        # item is up to date!
        issues_handled.add(item['content']['number'])
        continue

    # unknown item
    print(f"Unknown item: {issue.title}")

for issue in repo.get_issues(state="open"):
    if label_unmanaged in issue.labels:
        continue
    if issue.number in issues_handled:
        continue
    if issue.title.startswith("Implement "):
        print(f"Creating item: {issue.title}")
        if not DRY_RUN:
            item_id = add_project_item(PROJECT_ID, get_issue_id(issue.number))
            set_project_item_status(PROJECT_ID, item_id, STATUS_ID, STATUS_TODO_ID)
        continue
    
    print(f"Unknown issue: {issue.title}")
