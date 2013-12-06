import cv2

_templates = {
  '43':  [
    ('-1', cv2.imread('templates/stage1_43.png',0)),
    ('-2', cv2.imread('templates/stage2_43.png',0)),
    ('-3', cv2.imread('templates/stage3_43.png',0)),
    ('-4', cv2.imread('templates/stage4_43.png',0)),
    ('Mines', cv2.imread('templates/mines_43.png',0)),
    ('Jungle', cv2.imread('templates/jungle_43.png',0)),
    ('Ice Caves', cv2.imread('templates/icecaves_43.png',0)),
    ('Temple', cv2.imread('templates/temple_43.png',0)),
    ('Hell', cv2.imread('templates/hell_43.png',0)),
    ('Black Market', cv2.imread('templates/blackmarket_43.png',0)),
    ('Worm', cv2.imread('templates/worm_43.png',0)),
    ('Haunted Castle', cv2.imread('templates/castle_43.png',0)),
    ('Yama\'s Throne', cv2.imread('templates/yamasthrone_43.png',0)),
    ('Mothership', cv2.imread('templates/mothership_43.png',0)),
    ('City of Gold', cv2.imread('templates/cityofgold_43.png',0)),
    ('Olmec\'s Lair', cv2.imread('templates/olmecslair_43.png',0)),
    ('skull', cv2.imread('templates/skull_43.png',0)),
    ('Winner', cv2.imread('templates/winner_43.png',0)),
    ('Big Winner', cv2.imread('templates/bigwinner_43.png',0))
  ],

  '85':  [
    ('-1', cv2.imread('templates/stage1_85.png',0)),
    ('-2', cv2.imread('templates/stage2_85.png',0)),
    ('-3', cv2.imread('templates/stage3_85.png',0)),
    ('-4', cv2.imread('templates/stage4_85.png',0)),
    ('Mines', cv2.imread('templates/mines_85.png',0)),
    ('Jungle', cv2.imread('templates/jungle_85.png',0)),
    ('Ice Caves', cv2.imread('templates/icecaves_85.png',0)),
    ('Temple', cv2.imread('templates/temple_85.png',0)),
    ('Hell', cv2.imread('templates/hell_85.png',0)),
    ('Black Market', cv2.imread('templates/blackmarket_85.png',0)),
    ('Worm', cv2.imread('templates/worm_85.png',0)),
    ('Haunted Castle', cv2.imread('templates/castle_85.png',0)),
    ('Yama\'s Throne', cv2.imread('templates/yamasthrone_85.png',0)),
    ('Mothership', cv2.imread('templates/mothership_85.png',0)),
    ('City of Gold', cv2.imread('templates/cityofgold_85.png',0)),
    ('Olmec\'s Lair', cv2.imread('templates/olmecslair_85.png',0)),
    ('skull', cv2.imread('templates/skull_85.png',0)),
    ('Winner', cv2.imread('templates/winner_85.png',0)),
    ('Big Winner', cv2.imread('templates/bigwinner_85.png',0))
  ],

  '169': [
    ('-1', cv2.imread('templates/stage1_169.png',0)),
    ('-2', cv2.imread('templates/stage2_169.png',0)),
    ('-3', cv2.imread('templates/stage3_169.png',0)),
    ('-4', cv2.imread('templates/stage4_169.png',0)),
    ('Mines', cv2.imread('templates/mines_169.png',0)),
    ('Jungle', cv2.imread('templates/jungle_169.png',0)),
    ('Ice Caves', cv2.imread('templates/icecaves_169.png',0)),
    ('Temple', cv2.imread('templates/temple_169.png',0)),
    ('Hell', cv2.imread('templates/hell_169.png',0)),
    ('Black Market', cv2.imread('templates/blackmarket_169.png',0)),
    ('Worm', cv2.imread('templates/worm_169.png',0)),
    ('Haunted Castle', cv2.imread('templates/castle_169.png',0)),
    ('Yama\'s Throne', cv2.imread('templates/yamasthrone_169.png',0)),
    ('Mothership', cv2.imread('templates/mothership_169.png',0)),
    ('City of Gold', cv2.imread('templates/cityofgold_169.png',0)),
    ('Olmec\'s Lair', cv2.imread('templates/olmecslair_169.png',0)),
    ('skull', cv2.imread('templates/skull_169.png',0)),
    ('Winner', cv2.imread('templates/winner_169.png',0)),
    ('Big Winner', cv2.imread('templates/bigwinner_169.png',0))
  ]
}

def get_templates(key="169"):
  return _templates.get(str(key), _templates['169'])
