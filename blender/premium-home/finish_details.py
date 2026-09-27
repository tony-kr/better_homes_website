"""Final visual repairs; called from the builder and one-time scene repair."""
# Ground the terrace table with two deliberate solid oak pedestals.
for xx in (6.35,7.65):box('Terrace table pedestal',(xx,-2,.3375),(.16,.7,.675),'Oak',.025)
# Shelf boards terminate at uprights, avoiding coplanar intersections on their fronts.
remove_prefix('Study shelf','Wardrobe shelf')
for z in (.08,.65,1.23,1.81,2.4,2.82):
 for a,b in ((9.4475,11.1725),(11.2275,12.9525)):box('Fitted study shelf',(8.57,(a+b)/2,z),(.45,b-a,.045),'Oak',.004)
# Restore backing removed by prefix match above.
box('Study backing',(8.78,11.2,1.45),(.08,3.6,2.8),'Oak',.008)
for z in (.1,2.23,2.78):
 for a,b in ((8.1325,9.0175),(9.0625,9.9375),(9.9825,10.8675)):box('Fitted wardrobe shelf',(19.47,(a+b)/2,z),(.78,b-a,.045),'Oak',.004)
# Replace rectangular garment placeholders with a draped shirt silhouette.
old=[o for o in scene.objects if o.name.startswith('Hanging linen garment')]
for index,o in enumerate(old):
 cx,cy,cz=o.location;material=o.data.materials[0];bpy.data.objects.remove(o,do_unlink=True)
 # Counter-clockwise shirt outline in the rail's vertical plane.
 outline=[(-.095,1.84),(-.22,1.87),(-.39,1.63),(-.29,1.56),(-.205,1.65),(-.205,1.06),(.205,1.06),(.205,1.65),(.29,1.56),(.39,1.63),(.22,1.87),(.095,1.84),(0,1.76)]
 verts=[(cx,cy-.023,1.5)]+[(cx+x,cy+.02*math.sin(x*25+z*14),z) for x,z in outline]
 faces=[(0,i+1,(i+1)%len(outline)+1) for i in range(len(outline))]
 me=bpy.data.meshes.new('Draped cotton shirt');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new('Hanging cotton shirt',me);scene.collection.objects.link(ob);me.materials.append(material)
 solid=ob.modifiers.new('Fabric body','SOLIDIFY');solid.thickness=.012
 bevel=ob.modifiers.new('Soft garment edges','BEVEL');bevel.width=.007;bevel.segments=2
 for p in me.polygons:p.use_smooth=True
# Laundry joinery reads as fitted cabinetry, with separate doors and pulls.
for yy in (1.5,2.25,3,3.75,4.5):
 box('Laundry upper cabinet door',(19.125,yy,1.65),(.035,.725,1.34),'Oak',.008)
 box('Laundry cabinet pull',(19.09,yy-.25,1.48),(.03,.018,.27),'Bronze',.003)
