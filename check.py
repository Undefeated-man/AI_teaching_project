import logging, os

# make sure there's a directory called "log"
if not os.path.exists("./log"):
    os.mkdir("./log")
    
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', \
                        datefmt='%a, %d %b %Y %H:%M:%S', filename="log/debug.log", filemode='a')    # initialize the format 


class CheckRight:
    """
        使用说明：
            from check import CheckRight  # 导入类
            cr = CheckRight(<your dictionary here>)  # 使用
            cr.check()
        
        Inputs:
            d: a dictionary, {
                    "question": <question here>,
                    "answer": <user's answer here>
                }
        
        Returns:
            bool
    """
    def __init__(self, d):
        try:
            self.q = d["question"]
            self.a = d["answer"]
        except Exception as e:
            logging.warning(e)
        self.result_ls = []
        self.data = {"Lunch is on me": ["I'll pay for lunch.", "I pay for lunch."]}
        self.state = False
    
    def check(self):
        try:
            for ans in self.data[self.q]:
                if self.a in ans:
                    self.result_ls.append(True)
                else:
                    self.result_ls.append(False)
        except Exception as e:
            logging.warning(e)
        
        if True in self.result_ls:
            self.state = True
        
        return self.state


if __name__ == "__main__":
    cr = CheckRight({"question":"Lunch is on me", "answer": "I pay for lunch."})
    print(cr.check())
    input()