
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'DEVOLVER DOLLAR LBRACE RBRACE REFRESCOprograma : LBRACE contenido RBRACEcontenido : accion contenidocontenido : emptyaccion : DOLLARaccion : REFRESCOaccion : DEVOLVERaccion : LBRACE contenido RBRACEempty :'
    
_lr_action_items = {'LBRACE':([0,2,3,5,7,8,9,13,],[2,3,3,3,-4,-5,-6,-7,]),'$end':([1,11,],[0,-1,]),'DOLLAR':([2,3,5,7,8,9,13,],[7,7,7,-4,-5,-6,-7,]),'REFRESCO':([2,3,5,7,8,9,13,],[8,8,8,-4,-5,-6,-7,]),'DEVOLVER':([2,3,5,7,8,9,13,],[9,9,9,-4,-5,-6,-7,]),'RBRACE':([2,3,4,5,6,7,8,9,10,12,13,],[-8,-8,11,-8,-3,-4,-5,-6,13,-2,-7,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'programa':([0,],[1,]),'contenido':([2,3,5,],[4,10,12,]),'accion':([2,3,5,],[5,5,5,]),'empty':([2,3,5,],[6,6,6,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> programa","S'",1,None,None,None),
  ('programa -> LBRACE contenido RBRACE','programa',3,'p_programa','maquina_expendedora.py',42),
  ('contenido -> accion contenido','contenido',2,'p_contenido_con_accion','maquina_expendedora.py',67),
  ('contenido -> empty','contenido',1,'p_contenido_vacio','maquina_expendedora.py',129),
  ('accion -> DOLLAR','accion',1,'p_accion_dollar','maquina_expendedora.py',147),
  ('accion -> REFRESCO','accion',1,'p_accion_refresco','maquina_expendedora.py',164),
  ('accion -> DEVOLVER','accion',1,'p_accion_devolver','maquina_expendedora.py',182),
  ('accion -> LBRACE contenido RBRACE','accion',3,'p_accion_bloque','maquina_expendedora.py',199),
  ('empty -> <empty>','empty',0,'p_empty','maquina_expendedora.py',240),
]
