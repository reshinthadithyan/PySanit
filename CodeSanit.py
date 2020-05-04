import ast
import os
import json


class ParseLit(ast.NodeVisitor):
    def __init__(self):
        self.Func = {}
        self.stats = {"import": [], "from": []}
    def visit_Import(self, node):
        for alias in node.names:
            self.stats["import"].append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.stats["from"].append(alias.name)
        self.generic_visit(node)
    def visit_FunctionDef(self,node):
        Key = node.name
        if Key not in self.Func:
            self.Func[Key] = []
        Body = node.body
        for i in Body:
            if isinstance(i,ast.Assign):
                Hash = i.value
                if isinstance(Hash,ast.Call):
                    Need = Hash.func.id
                    if Need not in self.stats['import'] and Need not in self.stats['from']:
                        self.Func[Key].append(Need)    
    def report_Function(self):
        return self.Func


class CodeSanit():
    def __init__(self):
        self.Function_Check = None
        self.Missed = None
        self.Function_Dict = None
    def Func_Sanity(self,Diction):
        All_Func = list(Diction.keys())
        Missed = {}
        for Func in Diction:
            for Ind_Call in Diction[Func]:
                if Ind_Call not in Diction:
                    if Ind_Call not in Missed:
                        Missed[Ind_Call] = []
                    else:
                        pass
                    Missed[Ind_Call].append(Func)
        return Missed #A Dictionary Wherein Key is the missing function and Value of the key are the calls made within functions.
    def Parse_Check(self,Text):
        Dict = ast.parse(Text)
        Lit_Parse = ParseLit()
        Lit_Parse.visit(Dict)
        self.Function_Dict = Lit_Parse.report_Function()
        self.Function_Check = self.Func_Sanity(self.Function_Dict)
        return self.Function_Check
    def Check_File(self,Directory):
        with open(Directory, "r") as source:
            File_String = source.read()
        Sanit_File  =  self.Parse_Check(File_String)
        return Sanit_File
    def Check_Dir(self,Com_Dir):
        Output_Dict = {}
        self.Major_Dir = Com_Dir
        Directory = os.listdir(Com_Dir)
        for File in Directory:
            Output_Dict[File] = self.Check_File(Com_Dir+'/'+File)
        self.Log = Output_Dict
        return Output_Dict
    def Save_Json(self):        
        Save_File = self.Major_Dir+'.json'
        Json_Dict = json.dumps(self.Log)
        f = open(Save_File, "w")
        f.write(Json_Dict)
        return None

#Main

Sanit = CodeSanit()
Sanit.Check_Dir('G:\Python Parse\Test Folder')
Sanit.Save_Json()