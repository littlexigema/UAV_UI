import json

def main():
    dic={}
    with open('temporary_save','w') as file_obj:
        json.dump(dic,file_obj)
    with open('communication','w') as file_obj:
        json.dump(dic,file_obj)
    with open('verify','w') as file_obj:
        json.dump(dic,file_obj) 

if __name__=='__main__':
    main()

