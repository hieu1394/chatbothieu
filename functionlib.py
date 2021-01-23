from datetime import date, datetime
import re, random, string
import math
import chatterbot
import chatterbot.trainers, chatterbot.filters
import importlib
import conversionlib
import databasevar
appbot_state = False


def preprocess(Input):
    return Input

def processInput(Input):
    importlib.reload(databasevar)
    var = databasevar.Variables()
    politelist = [(" ạ", var.polite), ("", max(100 - var.polite,0))]
    polite = Probability(politelist)
    input = Input.lower()
    app_answer = False
    output = ""
    #Chào hỏi
    if compare(input,("xin chào","hello","chào "+ var.botrelative)):
        output = "Xin chào" + " " + var.bossrelative + polite
    elif compare(input, (var.botrelative + " ơi", var.botname+ " ơi")):
        output = Probability(("ơi","vâng","dạ",var.botrelative + " nghe", var.bossrelative + " nói đi"))
    #Thời gian
    elif compare(input,("hôm nay","ngày mấy"),"and"):
        today = date.today()
        day_string = today.strftime("%d/%m/%Y")
        output = "Hôm nay là ngày " + str(day_string)
    elif "mấy giờ rồi" in input:
        now = datetime.now()
        dt_string = now.strftime("%H:%M:%S %d/%m/%Y")
        output = "Ngày và giờ hiện tại là "+ str(dt_string)
    #Hỏi
    elif compare(input,(var.botrelative + " tên là gì",var.botrelative + " tên gì")):
        output = var.botrelative + " tên là " + var.botname + polite
    elif compare(input,(var.botrelative + " sinh năm nào", var.botname + " sinh năm nào")):
        output = "%s sinh năm %d%s"%(var.botrelative, var.botbirthyear, polite)
    elif compare(input,(var.botrelative + " bao nhiêu tuổi",var.botname + " bao nhiêu tuổi")):
        today = date.today()
        day_string = today.strftime("%Y")
        botage = int(day_string) - var.botbirthyear
        output = "%s %d tuổi%s"%(var.botrelative, botage, polite)
    elif (var.botrelative + " đang cảm thấy thế nào") in input:
        output = var.botrelative + " đang cảm thấy " +  var.botfeeling + polite
    elif compare(input,(var.botrelative + " có yêu " + var.bossrelative + " không",
                        var.botname + " có yêu " + var.bossrelative + " không")):
        output = var.botrelative + " " + var.loving + " " + var.bossrelative + polite
        change_Database('(self\.lovingpoint = ).{1,}', '\g<1>%d' % (var.lovingpoint+1))
    elif compare(input,(var.botrelative,"thích "," không"),"and"):
        try:
            like = re.search('thích (.{1,20}) không',input).group(1)
            botlike = "không"
            for liking, point in var.likinglist:
                if like == liking:
                    botlike = measure(point, var.likingtype)
            output = botlike + polite
        except Exception:
            app_answer = True
    elif compare(input,(var.botrelative,"thích "," nhất"),"and"):
        botlike = get_max(var.likinglist)
        output = Probability([(var.botrelative + " thích " + botlike + " nhất" + polite, 1),
                              (var.botrelative + " thích nhất là " + botlike + polite, 1)])
        add_conver_lib(output)
    #Thiết lập
    elif "anh tên là " in input:
        bossname = re.search('(tên|là)(( [AÀẢÃÁẠĂẰẲẴẮẶÂẦẨẪẤẬBCDĐEÈẺẼÉẸÊỀỂỄẾỆFGHIÌỈĨÍỊJKLMNOÒỎÕÓỌÔỒỔỖỐỘƠỜỞỠỚỢ'
                             'PQRSTUÙỦŨÚỤƯỪỬỮỨỰVWXYỲỶỸÝỴZ][aàảãáạăằẳẵắặâầẩẫấậbcdđeèẻẽéẹêềểễếệfghiìỉĩíịjklmn'
                             'oòỏõóọôồổỗốộơờởỡớợpqrstuùủũúụưừửữứựvwxyỳỷỹýỵz]{0,6}){1,5})',Input).group(2).lstrip()
        change_Database('(self\.bossname = ).{1,}', '\g<1>"%s"' % bossname)
        output = var.botrelative + " đã hiểu"
    elif compare(input,("trả lời hay","trả lời tốt")):
        add_conver_lib(var.lastAnswer)
        output = "cảm ơn anh"
    elif input=='exit':
        exit()
    else:
        app_answer = True
    if app_answer == True:
        output = appbot_answer(Input)
    Output = output.capitalize()
    change_Database('(self\.lastInput = ).{1,}', '\g<1>"%s"' % Input)
    change_Database('(self\.lastAnswer = ).{1,}', '\g<1>"%s"' % Output)
    Output_full = var.botname + ": " + Output
    return Output_full


def Probability(list):
    ProbabilityList = [content for content, weight in list for i in range(weight)]
    choice = random.choice(ProbabilityList)
    return choice


def measure(points,list,pointmax = 100):
    unit = pointmax/len(list)
    if points==pointmax:
        num = len(list)-1
    else:
        num =  math.floor(points/unit)
    return list[num]


def change_Database(pattern,replace):
    file_object = open('databasevar.py', mode="r", encoding='utf-8')
    file_read = file_object.read()
    file_edited = re.sub(pattern, replace, file_read)
    file_object.close()
    file_object = open('databasevar.py', mode="w", encoding='utf-8')
    file_object.write(file_edited)
    file_object.close()


def add_conver_lib(answer):
    file_object = open('conversionlib.py', mode="r", encoding='utf-8')
    file_read = file_object.readlines()
    file_object.close()
    line_edited = '    "%s",\n]'%answer
    file_edited = file_read[:len(file_read)-1]
    file_edited.append(line_edited)
    file_object = open('conversionlib.py', mode="w", encoding='utf-8')
    file_object.writelines(file_edited)
    file_object.close()


def compare( input, optionlist, andor = "or",cap = False):
    if andor == "and":
        boolean = True
        for option in optionlist:
            if not cap:
                if option.lower() not in input:
                    boolean = False
                    break
            else:
                if option not in input:
                    boolean = False
                    break
    else:
        boolean = False
        for option in optionlist:
            if not cap:
                if option.lower() in input:
                    boolean = True
                    break
            else:
                if option in input:
                    boolean = True
                    break
    return boolean


def appbot_answer(ask):
    bot = chatterbot.ChatBot('Bot', tagger_language=chatterbot.languages.VIE,
                             storage_adapter="chatterbot.storage.SQLStorageAdapter",
                             logic_adapters=[
                                 'chatterbot.logic.MathematicalEvaluation',
                                 #'chatterbot.logic.TimeLogicAdapter',
                                 'chatterbot.logic.BestMatch'
                             ],
                             database_uri='sqlite:///database.db',
                             filters = [chatterbot.filters.get_recent_repeated_responses]
                             )
    trainer = chatterbot.trainers.ListTrainer(bot,show_training_progress=False)
    importlib.reload(conversionlib)
    conversion = conversionlib.conversion
    trainer.train(conversion)
    answer = bot.get_response(ask).text
    return answer
def get_max(list):
    listpoint = []
    for i, (text, point) in enumerate(list):
        listpoint.append(point)
    textmax = list[listpoint.index(max(listpoint))][0]
    return textmax

