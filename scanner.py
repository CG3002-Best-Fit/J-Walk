class Scanner:
    source = ""
    index = 0
    def __init__(self, source):
        self.source = source
        self.index = 0
        
    def nextInt(self):
        while self.isAvailable() and ((self.source[self.index] == '\n') or (self.source[self.index] == '\r') or (self.source[self.index] == ' ')):
            self.index += 1
        ans = ""
        while self.isAvailable() and ((self.source[self.index] != '\n') and (self.source[self.index] != '\r') and (self.source[self.index] != ' ')):
            ans += self.source[self.index]
            self.index += 1
        if ans == "":
            return 0
        else :
            return int(ans)
    
    def isAvailable(self):
        return self.index < len(self.source)
    
if __name__ == '__main__':
    sc = Scanner("12\n123\n345\n678\n564")
    print sc.nextInt()
    print sc.nextInt()
    print sc.nextInt()
    print sc.nextInt()
    print sc.nextInt()
    