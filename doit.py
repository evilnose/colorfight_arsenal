from cf_client import Game

if __name__ == '__main__':
    g = Game()
    s = "UI大师"
    for i in range(len(s)):
        print(g.join('0' + s[i], 'http://colorfightuw.herokuapp.com/'))
