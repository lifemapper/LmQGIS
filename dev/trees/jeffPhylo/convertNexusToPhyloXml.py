"""
@summary: This script will convert a Nexus file from Jeff into Phylo-XML
@author: CJ Grady
@version: 1.0
@status: alpha

@license: gpl2
@copyright: Copyright (C) 2014, University of Kansas Center for Research

          Lifemapper Project, lifemapper [at] ku [dot] edu, 
          Biodiversity Institute,
          1345 Jayhawk Boulevard, Lawrence, Kansas, 66045, USA
   
          This program is free software; you can redistribute it and/or modify 
          it under the terms of the GNU General Public License as published by 
          the Free Software Foundation; either version 2 of the License, or (at 
          your option) any later version.
  
          This program is distributed in the hope that it will be useful, but 
          WITHOUT ANY WARRANTY; without even the implied warranty of 
          MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
          General Public License for more details.
  
          You should have received a copy of the GNU General Public License 
          along with this program; if not, write to the Free Software 
          Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 
          02110-1301, USA.
"""
from LmCommon.common.elementTreeLM import Element, SubElement, tostring

nexusFn = 'bats.nex'

#nexusTree = "TREE Fig._3_and_15.1 = [&R] (outgroup_to_Chiroptera,(((((((((Eptesicus_serotinus,Eptesicus_hottentotus,Eptesicus_furinalis,Eptesicus_fuscus,Eptesicus_bottae,Eptesicus_brasiliensis,(Eptesicus_diminutus,Eptesicus_innoxius),Eptesicus_guadeloupensis,Eptesicus_tatei,Eptesicus_demissus,Eptesicus_pachyotis,Eptesicus_kobayashii,Eptesicus_platyops),(Eptesicus_nilssoni,Eptesicus_bobrinskoi),Eptesicus_nasutus),Eptesicus_floweri),((((((Pipistrellus_pipistrellus,Pipistrellus_nathusii,Pipistrellus_permixtus),((Pipistrellus_javanicus,Pipistrellus_babu,Pipistrellus_endoi,Pipistrellus_paterculus,Pipistrellus_peguensis),(Pipistrellus_mimus,Pipistrellus_tenuis,Pipistrellus_coromandra,Pipistrellus_sturdeei))),(Pipistrellus_kuhlii,Pipistrellus_aero,Pipistrellus_aegyptius,Pipistrellus_inexspectatus,Pipistrellus_maderensis,Pipistrellus_rusticus),(Pipistrellus_ceylonicus,Pipistrellus_minahassae)),(Pipistrellus_rueppelli,Pipistrellus_crassulus,Pipistrellus_nanulus)),((((Pipistrellus_ariel,Pipistrellus_bodenheimeri,Pipistrellus_savii),Pipistrellus_macrotis,Pipistrellus_cadornae),((Pipistrellus_nanus,Pipistrellus_arabicus),Pipistrellus_imbricatus),(Pipistrellus_hesperus,Pipistrellus_musciculus),(Pipistrellus_eisentrauti,Pipistrellus_anchietai),(Pipistrellus_pulveratus,(Pipistrellus_kitcheneri,Pipistrellus_lophurus))),(Pipistrellus_stenopterus,Pipistrellus_anthonyi,Pipistrellus_joffrei)),((Eptesicus_somalicus,Eptesicus_capensis,Eptesicus_brunneus,Eptesicus_guineensis,Eptesicus_melckorum),(Eptesicus_tenuipinnis,Eptesicus_flavescens,Eptesicus_rendalli)),(Pipistrellus_tasmaniensis,(Pipistrellus_affinis,Pipistrellus_mordax,Pipistrellus_petersi)),(Pipistrellus_circumdatus,Pipistrellus_cuprosus,Pipistrellus_societatis),(Eptesicus_baverstocki,Eptesicus_douglasorum,Eptesicus_pumilus,Eptesicus_regulus,Eptesicus_vulturnus,Eptesicus_sagittula)),Pipistrellus_dormeri),(Nyctalus_noctula,Nyctalus_leisleri,Nyctalus_lasiopterus,Nyctalus_aviator,Nyctalus_azoreum,Nyctalus_montanus),((Barbastella_barbastellus,Barbastella_leucomelas),(((Plecotus_rafinequii,(Plecotus_townsendii,Plecotus_mexicanus)),((Plecotus_austriacus,Plecotus_teneriffae),(Plecotus_auritus,Plecotus_taivanus))),(Idionycteris_phyllotis,Euderma_maculatum))),Pipistrellus_subflavus,Myotis,Lasionycteris_noctivagans,(((Lasiurus_borealis,Lasiurus_seminolus),Lasiurus_cinereus,Lasiurus_castaneus),(Lasiurus_ega,Lasirus_intermedius),Lasiurus_egregius),((((Rhogessa_tumida,Rhogeesa_parvula,Rhogessa_minutilla,Rhogessa_genowaysi),Rhogessa_gracilis),Rhogessa_mira),Rhogeesa_alleni),Antrozidae,Nycticeus_humeralis,Otonycteris_hemprichi,(((Scotoecus_albofuscus,Scotoecus_hirundo),Scotoecus_pallidus),((Nycticeus_balstoni,(Nycticeus_sanborni,Nycticeus_greyii)),Nycticeus_schlieffeni)),((Nyctophilus_geoffroyi,Nyctophilus_timorensis,Nyctophilus_walkeri,Nyctophilus_arnhenmensis,Nyctophilus_gouldi,Nyctophilus_microdon,Nyctophilus_microtis,Nyctophilus_heran),Pharotis_imogene),((Scotophilus_kuhlii,(Scotophilus_heathii,Scotophilus_celebensis),(Scotophilus_leucogaster,(Scotophilus_dinganii,Scotophilus_nux,Scotophilus_robustus)),Scotophilus_nigrita,(Scotophilus_viridis,Scotophilus_borbonicus)),(Scotomanes_ornatus,Scotomanes_emarginatus)),(Vespertilio_murinus,Vespertilio_superans),(Murinae,Kerivoulinae),Nycticeus_rueppellii,((Chalinolobus_gouldii,Chalinolobus_morio,Chalinolobus_nigrogriseus,Chalinolobus_picatus,Chalinolobus_dwyeri),Chalinolobus_tuberculatus),Philetor_brachypterus,(Hesperoptenus_doriae,(Hesperoptenus_blanfordi,Hesperoptenus_tickelli,Hesperoptenus_tomesi,Hesperoptenus_gaskelli)),(Histiotus_velatus,Histiotus_montanus,Histiotus_macrotis,Histiotus_alienus),Eudiscopus_denticulus,Ia_io,(Glischropus_tylopus,Glischropus_javanus),(Laephotis_wintonii,Laephotis_botswannae,Laephotis_namibensis,Laephotis_angolensis),(Tylonycteris_pachypus,Tylonycteris_robustula),Mimetillus_moloneyi,(Chalinolobus_argentatus,Chalinolobus_beatrix,Chalinolobus_poensis,Chalinolobus_variegatus,Chalinolobus_alboguttatus,Chalinolobus_egeria,Chalinolobus_gleni,Chalinolobus_kenyacola,Chalinolobus_superbus)),Miniopterinae),(Tomopeatinae,Molossidae)),(((Phyllostomidae,Mormoopidae),Noctilionidae),Mystacinidae),Myzopodidae,(Thyropteridae,(Fuuripteridae,Natalidae))),(Emballonuridae,(((Rhinopoma_muscatellum,Rhinopoma_microphyllum,Rhinopoma_hardwickii),Craseonycteridae),((Nycteridae,(Rhinolophidae,Hipposideridae)),Megadermatidae)))),Pteropodidae));"
nexusTreeMod = "outgroup_to_Chiroptera,(((((((((Eptesicus_serotinus,Eptesicus_hottentotus,Eptesicus_furinalis,Eptesicus_fuscus,Eptesicus_bottae,Eptesicus_brasiliensis,(Eptesicus_diminutus,Eptesicus_innoxius),Eptesicus_guadeloupensis,Eptesicus_tatei,Eptesicus_demissus,Eptesicus_pachyotis,Eptesicus_kobayashii,Eptesicus_platyops),(Eptesicus_nilssoni,Eptesicus_bobrinskoi),Eptesicus_nasutus),Eptesicus_floweri),((((((Pipistrellus_pipistrellus,Pipistrellus_nathusii,Pipistrellus_permixtus),((Pipistrellus_javanicus,Pipistrellus_babu,Pipistrellus_endoi,Pipistrellus_paterculus,Pipistrellus_peguensis),(Pipistrellus_mimus,Pipistrellus_tenuis,Pipistrellus_coromandra,Pipistrellus_sturdeei))),(Pipistrellus_kuhlii,Pipistrellus_aero,Pipistrellus_aegyptius,Pipistrellus_inexspectatus,Pipistrellus_maderensis,Pipistrellus_rusticus),(Pipistrellus_ceylonicus,Pipistrellus_minahassae)),(Pipistrellus_rueppelli,Pipistrellus_crassulus,Pipistrellus_nanulus)),((((Pipistrellus_ariel,Pipistrellus_bodenheimeri,Pipistrellus_savii),Pipistrellus_macrotis,Pipistrellus_cadornae),((Pipistrellus_nanus,Pipistrellus_arabicus),Pipistrellus_imbricatus),(Pipistrellus_hesperus,Pipistrellus_musciculus),(Pipistrellus_eisentrauti,Pipistrellus_anchietai),(Pipistrellus_pulveratus,(Pipistrellus_kitcheneri,Pipistrellus_lophurus))),(Pipistrellus_stenopterus,Pipistrellus_anthonyi,Pipistrellus_joffrei)),((Eptesicus_somalicus,Eptesicus_capensis,Eptesicus_brunneus,Eptesicus_guineensis,Eptesicus_melckorum),(Eptesicus_tenuipinnis,Eptesicus_flavescens,Eptesicus_rendalli)),(Pipistrellus_tasmaniensis,(Pipistrellus_affinis,Pipistrellus_mordax,Pipistrellus_petersi)),(Pipistrellus_circumdatus,Pipistrellus_cuprosus,Pipistrellus_societatis),(Eptesicus_baverstocki,Eptesicus_douglasorum,Eptesicus_pumilus,Eptesicus_regulus,Eptesicus_vulturnus,Eptesicus_sagittula)),Pipistrellus_dormeri),(Nyctalus_noctula,Nyctalus_leisleri,Nyctalus_lasiopterus,Nyctalus_aviator,Nyctalus_azoreum,Nyctalus_montanus),((Barbastella_barbastellus,Barbastella_leucomelas),(((Plecotus_rafinequii,(Plecotus_townsendii,Plecotus_mexicanus)),((Plecotus_austriacus,Plecotus_teneriffae),(Plecotus_auritus,Plecotus_taivanus))),(Idionycteris_phyllotis,Euderma_maculatum))),Pipistrellus_subflavus,Myotis,Lasionycteris_noctivagans,(((Lasiurus_borealis,Lasiurus_seminolus),Lasiurus_cinereus,Lasiurus_castaneus),(Lasiurus_ega,Lasirus_intermedius),Lasiurus_egregius),((((Rhogessa_tumida,Rhogeesa_parvula,Rhogessa_minutilla,Rhogessa_genowaysi),Rhogessa_gracilis),Rhogessa_mira),Rhogeesa_alleni),Antrozidae,Nycticeus_humeralis,Otonycteris_hemprichi,(((Scotoecus_albofuscus,Scotoecus_hirundo),Scotoecus_pallidus),((Nycticeus_balstoni,(Nycticeus_sanborni,Nycticeus_greyii)),Nycticeus_schlieffeni)),((Nyctophilus_geoffroyi,Nyctophilus_timorensis,Nyctophilus_walkeri,Nyctophilus_arnhenmensis,Nyctophilus_gouldi,Nyctophilus_microdon,Nyctophilus_microtis,Nyctophilus_heran),Pharotis_imogene),((Scotophilus_kuhlii,(Scotophilus_heathii,Scotophilus_celebensis),(Scotophilus_leucogaster,(Scotophilus_dinganii,Scotophilus_nux,Scotophilus_robustus)),Scotophilus_nigrita,(Scotophilus_viridis,Scotophilus_borbonicus)),(Scotomanes_ornatus,Scotomanes_emarginatus)),(Vespertilio_murinus,Vespertilio_superans),(Murinae,Kerivoulinae),Nycticeus_rueppellii,((Chalinolobus_gouldii,Chalinolobus_morio,Chalinolobus_nigrogriseus,Chalinolobus_picatus,Chalinolobus_dwyeri),Chalinolobus_tuberculatus),Philetor_brachypterus,(Hesperoptenus_doriae,(Hesperoptenus_blanfordi,Hesperoptenus_tickelli,Hesperoptenus_tomesi,Hesperoptenus_gaskelli)),(Histiotus_velatus,Histiotus_montanus,Histiotus_macrotis,Histiotus_alienus),Eudiscopus_denticulus,Ia_io,(Glischropus_tylopus,Glischropus_javanus),(Laephotis_wintonii,Laephotis_botswannae,Laephotis_namibensis,Laephotis_angolensis),(Tylonycteris_pachypus,Tylonycteris_robustula),Mimetillus_moloneyi,(Chalinolobus_argentatus,Chalinolobus_beatrix,Chalinolobus_poensis,Chalinolobus_variegatus,Chalinolobus_alboguttatus,Chalinolobus_egeria,Chalinolobus_gleni,Chalinolobus_kenyacola,Chalinolobus_superbus)),Miniopterinae),(Tomopeatinae,Molossidae)),(((Phyllostomidae,Mormoopidae),Noctilionidae),Mystacinidae),Myzopodidae,(Thyropteridae,(Fuuripteridae,Natalidae))),(Emballonuridae,(((Rhinopoma_muscatellum,Rhinopoma_microphyllum,Rhinopoma_hardwickii),Craseonycteridae),((Nycteridae,(Rhinolophidae,Hipposideridae)),Megadermatidae)))),Pteropodidae)"
nexusTree = "TREE Fig._3_and_15.1 = [&R] (F(A,B,(C,D)E))"# Need to process [&R] and ;

# (A,B,(C,D));                           # only leaf nodes are named
# (A,B,(C,D)E)F;                         # all nodes are named (internal nodes are E,F)
# F(A,B,(C,D));                          # no internal nodes named other than root are named e.g. E is not named 
# F(A,B,(C,D)E);                         # same as #2 but with root at beginning
# (F(A,B,(C,D)E));                       # root node enclosed by parentheses
# ((A,B,(C,D)E)F);                       # same as last one, with root enclosed but at end
# enclosed roots can also not have names for internal nodes (E)

def createClade(parent, depth, name=None):
   cladeEl = SubElement(parent, "clade", namespace=None)
   SubElement(cladeEl, "branch_length", value=depth, namespace=None)
   if name is not None:
      SubElement(cladeEl, "name", value=name, namespace=None)
   return cladeEl

def xmlify(parent, nexStr, depth=0):
   # Go until comma, that's a name
   # If encounter a '(', recurse, but only if the internal node or root node is unamed?
   # If encounter a ')', return
   i = 0
   name = ''
   while i < len(nexStr):
      n = nexStr[i]
      if n == '(':
         node = createClade(parent, depth)
         xmlify(node, nexStr[i+1:], depth=depth+1)
      elif n == ')':
         node = createClade(parent, depth, name=name)
         return
      elif n == ',':
         node = createClade(parent, depth, name=name)
         name = ''
      else:
         name = name + n
      i = i+1

def processNexusForPhyloXml(nexStr):
   if nexStr.startswith('TREE'):
      parts = nexStr.strip('TREE ').split(' = ')
      name = parts[0]
      phylo = parts[1]
      print "name ",name
      t = Element("phyloxml", namespace=None, 
               attribs=[
                        ("xmlns", "http://www.phyloxml.org"),
                        ("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance"),
                        ("xsi:schemaLocation", "http://www.phyloxml.org http://www.phyloxml.org/1.10/phyloxml.xsd")
                       ])
      phylogenyEl = SubElement(t, "phylogeny", namespace=None, attribs=[('rooted', 'true')])
      SubElement(phylogenyEl, 'name', value=name, namespace=None)
      xmlify(phylogenyEl, phylo.strip('[&R] '))
      return t

outStr = tostring(processNexusForPhyloXml(nexusTree))

with open('/home/jcavner/PhyloXM_Examples/testCJ.xml', 'w') as f:
   f.write(outStr)
   
      