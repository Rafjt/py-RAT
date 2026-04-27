import os


class SearchCommand:

    name = "search"

    def execute(self, args: str) -> str:

        parts = args.split()

        if not parts:
            return "Usage: search <pattern> [path]"

        pattern = parts[0]

        if len(parts) > 1:
            root = parts[1]
        else:
            root = os.getcwd()

        if not os.path.exists(root):
            return "Path not found"

        matches = []

        try:

            for dirpath, dirnames, filenames in os.walk(root):

                for name in filenames:

                    if pattern.lower() in name.lower():

                        full_path = os.path.join(
                            dirpath,
                            name,
                        )

                        matches.append(full_path)

        except Exception as e:

            return f"Search error: {e}"

        if not matches:
            return "No files found"

        return "\n".join(matches)
