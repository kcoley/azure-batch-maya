#-------------------------------------------------------------------------
#
# Azure Batch Maya Plugin
#
# Copyright (c) Microsoft Corporation.  All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#--------------------------------------------------------------------------

import os
import sys
import gzip
import json

from maya import cmds, mel

from default import AzureBatchRenderJob, AzureBatchRenderAssets


class AzureBatchMayaJob(AzureBatchRenderJob):

    render_engine = "mayaSoftware"

    def __init__(self):
        self._renderer = "sw"
        self.label = "Maya Software"

    def settings(self):
        if self.scene_name == "":
            job_name = "Untitled"
        else:
            job_name = str(os.path.splitext(os.path.basename(self.scene_name))[0])
        file_prefix = mel.eval("getAttr defaultRenderGlobals.imageFilePrefix")
        if file_prefix:
            file_prefix = os.path.split(file_prefix)[1]
        else:
            file_prefix = "<Scene>.<Camera>.<RenderLayer>"

        self.job_name = self.display_string("Job Name:   ", job_name)
        self.output_name = self.display_string("Output Prefix:   ", file_prefix)
        self.start = self.display_int("Start frame:   ", self.start_frame, edit=True)
        self.end = self.display_int("End frame:   ", self.end_frame, edit=True)
        self.step = self.display_int("Frame step:   ", self.frame_step, edit=True)

    def get_title(self):
        return str(cmds.textField(self.job_name, query=True, text=True))

    def render_enabled(self):
        return True

    def get_jobdata(self):
        if self.scene_name == '':
            raise ValueError("Current Maya scene has not been saved to disk.")
        
        pending_changes = cmds.file(query=True, modified=True)
        if not pending_changes:
            return self.scene_name, [self.scene_name]
        options = {
            'save': "Save and continue",
            'nosave': "Continue without saving",
            'cancel': "Cancel"
        }
        answer = cmds.confirmDialog(title="Unsaved Changes",
                                    message="There are unsaved changes. Continue?",
                                    button=options.values(),
                                    defaultButton=options['save'],
                                    cancelButton=options['cancel'],
                                    dismissString=options['cancel'])
        if answer == options['cancel']:
            raise Exception("Submission aborted")
        if answer == options['save']:
            cmds.SaveScene()
        return self.scene_name, [self.scene_name]

    def get_params(self):
        params = {}
        params["frameStart"] = cmds.intField(self.start, query=True, value=True)
        params["frameEnd"] = cmds.intField(self.end, query=True, value=True)
        params["frameStep"] = cmds.intField(self.step, query=True, value=True)
        params["renderer"] = self._renderer
        return params


class MayaRenderAssets(AzureBatchRenderAssets):

    assets = []
    render_engine = "mayaSoftware"

    def renderer_assets(self):
        return self.assets