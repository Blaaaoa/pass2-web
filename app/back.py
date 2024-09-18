from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def decimal_to_hex(decimal):
    return hex(decimal)[2:].upper()

def pass_one(src_code, optab):
    saved_labels = []
    symtab = []
    intermediate_file = []

    starting_address = 0
    location_counter = 0

    input_lines = [line.split() for line in src_code]
    optab_dict = optab

    if len(input_lines) == 0:
        return {"error": "Source code is empty"}, 400

    # Handle the starting address
    if input_lines[0][1] == "START":
        starting_address = int(input_lines[0][2], 16)
        location_counter = starting_address
    else:
        location_counter = 0
        starting_address = 0

    intermediate_file.append(f"-\t{input_lines[0][0]}\t{input_lines[0][1]}\t{input_lines[0][2]}")

    for i in range(1, len(input_lines)):
        if len(input_lines[i]) < 2:
            continue  # Skip lines that don't have enough data

        label, opcode, operand = input_lines[i]

        if opcode == "END":
            break

        # Handle labels
        if label != "-":
            if label in saved_labels:
                return {"error": f"Duplicate label: {label} found"}, 400
            else:
                saved_labels.append(label)
                symtab.append({"label": label, "address": decimal_to_hex(location_counter)})

        # Check opcode in optab
        if opcode in optab_dict:
            intermediate_file.append(f"{decimal_to_hex(location_counter)}\t{label}\t{opcode}\t{operand}")
            location_counter += 3  # Increment for instructions
        elif opcode == "BYTE":
            intermediate_file.append(f"{decimal_to_hex(location_counter)}\t{label}\t{opcode}\t{operand}")
            location_counter += len(operand) - 3  # Adjust for BYTE operands
        elif opcode == "RESB":
            intermediate_file.append(f"{decimal_to_hex(location_counter)}\t{label}\t{opcode}\t{operand}")
            location_counter += int(operand)  # Adjust for reserved bytes
        elif opcode == "WORD":
            intermediate_file.append(f"{decimal_to_hex(location_counter)}\t{label}\t{opcode}\t{operand}")
            location_counter += 3  # Increment for WORD instructions
        elif opcode == "RESW":
            intermediate_file.append(f"{decimal_to_hex(location_counter)}\t{label}\t{opcode}\t{operand}")
            location_counter += 3 * int(operand)  # Increment for reserved words
        else:
            return {"error": f"Invalid opcode: {opcode}"}, 400

    # Append the final END statement to intermediate file
    if len(input_lines) > 1:
        label, opcode, operand = input_lines[-1]
        intermediate_file.append(f"{decimal_to_hex(location_counter)}\t{label}\t{opcode}\t{operand}")

    return {"intermediate_file": intermediate_file, "symtab": symtab}

@app.route('/', methods=['POST'])
def process_pass_one():
    data = request.json

    # Debugging: Print received data
    print("Received Data:", data)

    if 'srccode' not in data or 'optab' not in data:
        return jsonify({"error": "Missing required fields: 'srccode' and 'optab'"}), 400

    src_code = data['srccode']
    optab = data['optab']

    # Process pass one
    result = pass_one(src_code, optab)
    
    if "error" in result:
        return jsonify(result), 400

    return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=True)
