SHARED_FILE_PATH = "D:\work\Anul3\SEM2\CLOUD\TEMA2\SharedFile.txt"
RESP_FORMAT = "HTTP/1.1 {0}\nContent-Type: text/html \n\n{1}"
RESP_FORMAT_ERROR = "HTTP/1.1 {0}\n"
ERROR_200 = "200 OK"
ERROR_201 = "201 Created"
ERROR_204 = "204 No Content"
ERROR_400 = "400 Bad Request"
ERROR_404 = "404 Not Found"
ERROR_405 = "405 Method not allowed"
ERROR_500 = "500 Internal server error"

""" Aux function """
def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    print(lines[line_num])
    lines[line_num] = text + "\n"
    print(lines[line_num])
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()

class func:

    @staticmethod
    def get(request):
        params = request["Params"]
        if "id" in params:
            row_index = int(params["id"])
        else:
            return RESP_FORMAT_ERROR.format(ERROR_400)
        file_object = open(SHARED_FILE_PATH, 'r')
        num_lines = sum(1 for line in file_object)
        file_object.seek(0)
        """ Check if the line exists """
        if row_index > num_lines or row_index < 0:
            file_object.close()
            return RESP_FORMAT_ERROR.format(ERROR_404)
        elif row_index < num_lines and row_index >= 0:
            lines = file_object.readlines()
            file_object.close()
            if len(lines[row_index]) == 0:
                file_object.close()
                return RESP_FORMAT_ERROR.format(ERROR_404)
            file_object.close()
            return RESP_FORMAT.format(ERROR_200, lines[row_index])

    @staticmethod
    def put(request):
        """ If the entry doesn't exist, it creates one.
            But if the provided index is greater, it will return an error.
            If it exists, it will replace all the content."""
        params = request["Params"]
        body = request["Body"]
        id_given = False
        num_lines = 0
        if "id" in params:
            id_given = True
            row_index = int(params["id"])
            file_object = open(SHARED_FILE_PATH, 'r')
            num_lines = sum(1 for line in file_object)
            file_object.seek(0)
            file_object.close()
        if id_given == False:
            """ Create a new entry in the file with the content from the body """
            with open(SHARED_FILE_PATH, "a") as myfile:
                for key in body:
                    myfile.write(key + ":" + body[key])
                    myfile.write("\n")
            return RESP_FORMAT_ERROR.format(ERROR_201)
        if id_given == True:
            if row_index < num_lines:
                lines = open(SHARED_FILE_PATH, 'r').readlines()
                line = (lines[row_index])
                words = line.split()
                keys = []
                for key in body:
                    if not key.isdigit():
                        return RESP_FORMAT.format(ERROR_400, "Index of word not a digit!")
                    key_copy = int(key)
                    keys.append(key_copy)
                    if key_copy + 1 > len(words):
                        return RESP_FORMAT.format(ERROR_404, "Not found word:{0} in line:{0}".format(key_copy, row_index))
                    word_value = body[key]
                    words[key_copy] = word_value
                line = ""
                for word in words:
                    line+=word
                    line+=" "
                replace_line(SHARED_FILE_PATH, row_index, line)
                return RESP_FORMAT_ERROR.format(ERROR_200)
            else:
                return RESP_FORMAT_ERROR.format(ERROR_404)

    @staticmethod
    def post(request):
        """ If the entry doesn't exist, it creates one.
            If it exists, it will append the given values to the specified entries: The parameter will mention the index of the line,
            the key in the body the number of the word, the value the new value of the specified word """
        params = request["Params"]
        body = request["Body"]
        id_given = False
        num_lines = 0
        if "id" in params:
            id_given = True
            row_index = int(params["id"])
            file_object = open(SHARED_FILE_PATH, 'r')
            num_lines = sum(1 for line in file_object)
            file_object.seek(0)
            file_object.close()
        if id_given == False:
            """ Create a new entry in the file with the content from the body """
            with open(SHARED_FILE_PATH, "a") as myfile:
                for key in body:
                    myfile.write(key + ":" + body[key])
                    myfile.write("\n")
            return RESP_FORMAT_ERROR.format(ERROR_201)
        if id_given == True:
            if row_index < num_lines:
                lines = open(SHARED_FILE_PATH, 'r').readlines()
                line = (lines[row_index])
                words = line.split()
                keys = []
                for key in body:
                    if not key.isdigit():
                        return RESP_FORMAT.format(ERROR_400, "Index of word not a digit!")
                    key_copy = int(key)
                    keys.append(key_copy)
                    if key_copy + 1 > len(words):
                        return RESP_FORMAT.format(ERROR_404, "Not found word:{0} in line:{0}".format(key_copy, row_index))
                    word_value = body[key]
                    words[key_copy] += word_value
                line = ""
                for word in words:
                    line+=word
                    line+=" "
                replace_line(SHARED_FILE_PATH, row_index, line)
                return RESP_FORMAT_ERROR.format(ERROR_200)
            else:
                return RESP_FORMAT_ERROR.format(ERROR_404)


    @staticmethod
    def delete(request):
        params = request["Params"]
        if "id" in params:
            row_index = int(params["id"])
        else:
            return RESP_FORMAT_ERROR.format(ERROR_400)
        file_object = open(SHARED_FILE_PATH, 'r')
        num_lines = sum(1 for line in file_object)
        file_object.seek(0)
        file_object.close()
        """ Check if the line exists """
        if row_index > num_lines or row_index < 0:
            return RESP_FORMAT_ERROR.format(ERROR_404)
        elif row_index < num_lines and row_index >= 0:
            with open(SHARED_FILE_PATH, "r+") as f:
                lines = f.readlines()
                del lines[row_index]
                f.seek(0)
                f.truncate()
                f.writelines(lines)
            return RESP_FORMAT_ERROR.format(ERROR_204)
