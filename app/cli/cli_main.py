from app.skills.greet import greet
from app.skills.calculator import calculate
from app.proposals.writer import write_proposal


def main() -> None:
    print("Welcome to Kimiko v1!")
    print("Type 'help' for commands or 'quit' to exit.")

    try:
        user_name = input("What's your name? ").strip()
    except KeyboardInterrupt:
        print("\nGoodbye.")
        return

    while True:
        try:
            user_input = input("> ").strip()
        except KeyboardInterrupt:
            print("\nInterrupted. Goodbye.")
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        if cmd in ("quit", "exit"):
            print("Goodbye!")
            break

        elif cmd == "help":
            print(
                "Commands:\n"
                "  help                 Show this help\n"
                "  greet                Greet you by name\n"
                "  calculate <expr>     Do basic math\n"
                "  propose              Propose a change or improvement\n"
                "  quit / exit          Exit Kimiko"
            )

        elif cmd == "greet":
            print(greet(user_name))

        elif cmd.startswith("calculate"):
            expression = user_input[len("calculate"):].strip()
            if not expression:
                print("Please provide a math expression.")
            else:
                print(calculate(expression))

        elif cmd == "propose":
            print("Let's write a proposal together.")

            title = input("Title: ").strip()
            description = input("Description: ").strip()
            files_raw = input("Affected files (comma-separated): ").strip()
            reason = input("Reason for change: ").strip()

            affected_files = [
                f.strip() for f in files_raw.split(",") if f.strip()
            ]

            path = write_proposal(
                title=title,
                description=description,
                affected_files=affected_files,
                reason=reason,
            )

            print(f"Proposal written to: {path}")

        else:
            print("Sorry, I didn't understand that command. Type 'help'.")


if __name__ == "__main__":
    main()
