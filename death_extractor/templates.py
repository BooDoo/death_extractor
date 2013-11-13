import cv2

_templates = {
'43':  [cv2.imread('templates/gameover_43.png',0), cv2.imread('templates/leaderboard_43.png',0), cv2.imread('templates/leaderboard-vines_43.png',0)], 
'85':  [cv2.imread('templates/gameover_85.png',0), cv2.imread('templates/leaderboard_85.png',0), cv2.imread('templates/leaderboard-vines_85.png',0)],
'169': [cv2.imread('templates/gameover.png',0),    cv2.imread('templates/leaderboard.png',0),    cv2.imread('templates/leaderboard-vines.png',0)]
}

def get_templates(key="169"):
  return _templates.get(str(key), _templates['169'])