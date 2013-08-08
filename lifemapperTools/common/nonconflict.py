"""
@license: gpl2
@copyright: Copyright (C) 2013, University of Kansas Center for Research

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
import inspect, types, __builtin__

############## preliminary: two utility functions #####################

def skip_redundant(iterable, skipset=None):
   "Redundant items are repeated items or items in the original skipset."
   if skipset is None: skipset = set()
   for item in iterable:
      if item not in skipset:
            skipset.add(item)
            yield item


def remove_redundant(metaclasses):
   skipset = set([types.ClassType])
   for meta in metaclasses: # determines the metaclasses to be skipped
      skipset.update(inspect.getmro(meta)[1:])
   return tuple(skip_redundant(metaclasses, skipset))

##################################################################
## now the core of the module: two mutually recursive functions ##
##################################################################

memoized_metaclasses_map = {}

def get_noconflict_metaclass(bases, left_metas, right_metas):
   """Not intended to be used outside of this module, unless you know
   what you are doing."""
   # make tuple of needed metaclasses in specified priority order
   metas = left_metas + tuple(map(type, bases)) + right_metas
   needed_metas = remove_redundant(metas)

   # return existing confict-solving meta, if any
   if needed_metas in memoized_metaclasses_map:
      return memoized_metaclasses_map[needed_metas]
   # nope: compute, memoize and return needed conflict-solving meta
   elif not needed_metas:         # wee, a trivial case, happy us
         meta = type
   elif len(needed_metas) == 1: # another trivial case
      meta = needed_metas[0]
   # check for recursion, can happen i.e. for Zope ExtensionClasses
   elif needed_metas == bases: 
         raise TypeError("Incompatible root metatypes", needed_metas)
   else: # gotta work ...
         metaname = '_' + ''.join([m.__name__ for m in needed_metas])
         meta = classmaker()(metaname, needed_metas, {})
   memoized_metaclasses_map[needed_metas] = meta
   return meta

def classmaker(left_metas=(), right_metas=()):
   def make_class(name, bases, adict):
      metaclass = get_noconflict_metaclass(bases, left_metas, right_metas)
      return metaclass(name, bases, adict)
   return make_class