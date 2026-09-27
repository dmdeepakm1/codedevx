from pathlib import Path
import subprocess

class WorkspaceTools:
    def __init__(self,root:str):
        self.root=Path(root).resolve()

    def _path(self,relative:str)->Path:
        p=(self.root/relative).resolve()
        if self.root not in p.parents and p != self.root:
            raise ValueError("Path escapes workspace")
        return p

    def read(self,relative:str)->str:
        return self._path(relative).read_text(encoding="utf-8")

    def write(self,relative:str,content:str)->None:
        p=self._path(relative); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(content,encoding="utf-8")

    def run(self,args:list[str],timeout:int=300)->dict:
        allowed={"pytest","python","python3","mvn","gradle","./gradlew","npm","pnpm","yarn","git"}
        if not args or args[0] not in allowed:
            raise ValueError("Command is not allow-listed")
        p=subprocess.run(args,cwd=self.root,text=True,capture_output=True,timeout=timeout)
        return {"returncode":p.returncode,"stdout":p.stdout[-20000:],"stderr":p.stderr[-20000:]}
