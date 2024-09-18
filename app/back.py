from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

@app.route('/run-code', methods=['POST'])
def run_code():
    LC = 0
    mnemonics = {
        'STOP': ('00', 'IS', 0), 'ADD': ('01', 'IS', 2), 'SUB': ('02', 'IS', 2), 
        'MUL': ('03', 'IS', 2), 'MOVER': ('04', 'IS', 2), 'MOVEM': ('05', 'IS', 2), 
        'COMP': ('06', 'IS', 2), 'BC': ('07', 'IS', 2), 'DIV': ('08', 'IS', 2), 
        'READ': ('09', 'IS', 1), 'PRINT': ('10', 'IS', 1), 'LTORG': ('05', 'AD', 0), 
        'ORIGIN': ('03', 'AD', 1), 'START': ('01', 'AD', 1), 'EQU': ('04', 'AD', 2), 
        'DS': ('01', 'DL', 1), 'DC': ('02', 'DL', 1), 'END': ('AD', 0)
    }
    REG = {'AREG': 1, 'BREG': 2, 'CREG': 3, 'DREG': 4}
    symtab = {}
    pooltab = []
    words = []
    symindex = 0

    def END():
        nonlocal LC
        pool = 0
        z = 0
        if os.path.exists("inter_code.txt"):
            os.remove("inter_code.txt")
        with open("inter_code.txt", "a") as ifp, open("literals.txt", "a+") as lit, open("tmp.txt", "a+") as tmp:
            lit.truncate(0)
            tmp.truncate(0)
            ifp.write("\t(AD,02)\n")
            lit.seek(0)
            for x in lit:
                if "**" in x:
                    pool += 1
                    if pool == 1:
                        pooltab.append(z)
                    y = x.split()
                    tmp.write(y[0] + "\t" + str(LC) + "\n")
                    LC += 1
                else:
                    tmp.write(x)
                z += 1
            lit.truncate(0)
            tmp.seek(0)
            for x in tmp:
                lit.write(x)
            tmp.truncate(0)
        return "END processing complete"

    def LTORG():
        nonlocal LC
        pool = 0
        z = 0
        with open("literals.txt", "a+") as lit, open("tmp.txt", "a+") as tmp:
            lit.seek(0)
            x = lit.readlines()
            i = 0
            while i < len(x):
                f = []
                if "**" in x[i]:
                    j = 0
                    pool += 1
                    if pool == 1:
                        pooltab.append(z)
                    while x[i][j] != "'":
                        j += 1
                    j += 1
                    while x[i][j] != "'":
                        f.append(x[i][j])
                        j += 1
                    if i != len(x) - 1:
                        ifp.write("\t(AD,05)\t(DL,02)(C," + str(f[0]) + ")\n")
                        y = x[i].split()
                        tmp.write(y[0] + "\t" + str(LC) + "\n")
                        LC += 1
                        ifp.write(str(LC))
                    else:
                        ifp.write("\t(AD,05)\t(DL,02)(C," + str(f[0]) + ")\n")
                        y = x[i].split()
                        tmp.write(y[0] + "\t" + str(LC) + "\n")
                        LC += 1
                else:
                    tmp.write(x[i])
                z += 1
                i += 1
            lit.truncate(0)
            tmp.seek(0)
            for x in tmp:
                lit.write(x)
            tmp.truncate(0)
        return "LTORG processing complete"

    def ORIGIN(addr):
        nonlocal LC
        with open("inter_code.txt", "a") as ifp:
            ifp.write("\t(AD,03)\t(C," + str(addr) + ")\n")
        LC = int(addr)
        return "ORIGIN processing complete"

    def DS(size):
        nonlocal LC
        with open("inter_code.txt", "a") as ifp:
            ifp.write("\t(DL,01)\t(C," + size + ")\n")
        LC += int(size)
        return "DS processing complete"

    def DC(value):
        nonlocal LC
        with open("inter_code.txt", "a") as ifp:
            ifp.write("\t(DL,02)\t(C," + value + ")\n")
        LC += 1
        return "DC processing complete"

    def OTHERS(mnemonic, k):
        nonlocal words, LC, symtab
        z = mnemonics[mnemonic]
        result = f"\t({z[1]},{z[0]})\t"
        y = z[-1]
        for i in range(1, y + 1):
            words[k + i] = words[k + i].replace(",", "")
            if words[k + i] in REG.keys():
                result += f"(RG,{REG[words[k + i]]})"
            elif "=" in words[k + i]:
                with open("literals.txt", "a+") as lit:
                    lit.seek(0, 2)
                    lit.write(words[k + i] + "\t**\n")
                    lit.seek(0)
                    x = lit.readlines()
                    result += f"(L,{len(x)})"
            else:
                if words[k + i] not in symtab.keys():
                    symtab[words[k + i]] = ("**", symindex)
                    result += f"(S,{symindex})"
                    symindex += 1
                else:
                    w = symtab[words[k + i]]
                    result += f"(S,{w[-1]})"
        result += "\n"
        LC += 1
        return result

    def detect_mn(k):
        nonlocal words, LC
        if words[k] == "START":
            LC = int(words[1])
            with open("inter_code.txt", "a") as ifp:
                ifp.write("\t(AD,01)\t(C," + str(LC) + ')\n')
        elif words[k] == 'END':
            return END()
        elif words[k] == "LTORG":
            return LTORG()
        elif words[k] == "ORIGIN":
            return ORIGIN(words[k + 1])
        elif words[k] == "DS":
            return DS(words[k + 1])
        elif words[k] == "DC":
            return DC(words[k + 1])
        else:
            return OTHERS(words[k], k)

    try:
        # Get the input from the request body
        data = request.json
        input_code = data.get('code', '')

        # Process the input code
        words = input_code.splitlines()
        result = []
        
        for line in words:
            words = line.split()
            if LC > 0:
                result.append(str(LC))
            if words[0] in mnemonics.keys():
                result.append(f"Mnemonic: {words[0]} - " + detect_mn(0))
            else:
                if words[0] not in symtab.keys():
                    symtab[words[0]] = (LC, symindex)
                    symindex += 1
                else:
                    x = symtab[words[0]]
                    if x[0] == "**":
                        symtab[words[0]] = (LC, x[1])
                result.append(detect_mn(1))
        
        # Save final results
        with open("SymTab.txt", "a+") as sym, open("PoolTab.txt", "a+") as pool:
            sym.truncate(0)
            for x in symtab:
                sym.write(x + "\t" + str(symtab[x][0]) + "\n")
            pool.truncate(0)
            for x in pooltab:
                pool.write(str(x) + "\n")
        
        if os.path.exists("tmp.txt"):
            os.remove("tmp.txt")
        
        return jsonify({'result': result})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
