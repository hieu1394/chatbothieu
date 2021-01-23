import importlib
import functionlib
import databasevar
import traceback

def main():
    global input_cmd, var
    while True:
        try:
            importlib.reload(databasevar)
            var = databasevar.Variables()
            importlib.reload(functionlib)
            preInput = functionlib.preprocess(input(var.bossname + ": "))
            importlib.reload(functionlib)
            output = functionlib.processInput(preInput)
            print(output)
        except Exception:
            traceback.print_exc()
            #break


if __name__ == "__main__":
    main()