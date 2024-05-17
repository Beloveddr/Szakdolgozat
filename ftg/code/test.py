import docs as doc

# dict = {"flame": 1, "heal": 0, "fart": 0}
# new_dict = {}
# for item in dict.keys():
#     if dict[item] > 0:
#         new_dict[item] = dict[item]
# if len(new_dict) < 1:
#     new_dict.update({"none": 1})
# print(new_dict)

# output = {'flame':
#               {'graphic': '../graphics/particles/flame/fire.png',
#                'name': 'nev1'},
#           'heal':
#               {'graphic': '../graphics/particles/heal/heal.png',
#                'name': 'nev2'},
#           'fart':
#               {'graphic': '../graphics/particles/fart/fart.png',
#                'name': 'nev3'
#                }
#           }
#
# indexes = {
#     0: "flame"
# }
# index = 0
# # print(output[indexes[index]]["name"])
#
# inp = {"flame": 1, "heal": 1}
# out = {"flame": 1, "heal": 1, "fart2": 1, "fart3": 1, "fart4": 1}
#
# inp_index = 1
# out_index = 2
#
# new_list_inp = []
# new_list_out = []
#
# for k in list(inp):
#     new_list_inp.append(k)
# for k in list(out):
#     new_list_out.append(k)
#
# new_list_inp[inp_index] = new_list_out[out_index]
# magic_hand = {}
# for k in new_list_inp:
#     magic_hand[k] = 1

# for i in [1,2,3]:
#     doc.create_doc(f"INDB slot{i} CRDOC doors", "id: int, doorid: string, islocked: int")

# drop_pos = {0: '(1440.0, 1888.0)',
#             2: '(1297.0, 1572.0)'}
#
# new_dict = {}
#
# new_index = 0
# for i in drop_pos:
#     new_dict[new_index] = drop_pos[i]
#     new_index+=1
#
# print(new_dict)

for i in [1,2,3]:
    doc.create_doc(f"INDB slot{i} CRDOC armor_inv", "id: int, itemid: int, isequiped: int, slotindex: int, type: string, pathid: int, quantity: string, descriptionid: int, dmgprotection: int, specialid: int, customid: int")

# for i in [1,2,3]:
#     # doc.create_doc(f"INDB slot{i} CRDOC chests", "id: int, map: string, isopen: int, itemid: int, quantity: int, groundid: int")
#     doc.add(f"map2,0,200,1,0 INDB slot{i} INTO chests")


# for i in [1,2,3]:
#     doc.add(f"map2-1,0,2100,1 INDB slot{i} INTO ground_objects")

# doc.add("Miki,42 INDB school INTO teachers")

