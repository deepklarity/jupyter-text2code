define([
    'jquery',
    'require',
    'base/js/namespace',
    'base/js/dialog',
    'base/js/events',
], function (
    $,
    requirejs,
    Jupyter,
    dialog,
    events
) {
    "use strict";

    var jupyter_text2code_lib = {}
    jupyter_text2code_lib.code_init = "";

    // define default values for config parameters
    var params = {
        jupyter_text2code_it_default_to_public: false,
    };

    var extension_state = {
        is_open: false,
        data: {
            query: "import all libraries",
            history: [],
            presets: [
                "help",
                "use dark theme",
                "import all libraries",
                "load (xxx.csv) in (df)",
                "pie plot of (column) in (df)",
                "bar plot of columns (column) & (column) in (df)",
                "list all columns of (df)",
                "show (x) rows of (df)"
            ]
        }
    };

    function code_exec_callback(query, response) {
        var generated_code = JSON.parse(response)["message"]

        extension_state.data.history.push({"query": query, "code": generated_code});
        update_history_display(query);

        var cur_cell = Jupyter.notebook.get_selected_cell();
        if (cur_cell.get_text() == ""){
            var command_cell = cur_cell;
        }else{
            var command_cell = Jupyter.notebook.insert_cell_below('code');
        }
        command_cell.select();
        command_cell.set_text(generated_code);
        command_cell.execute();
        Jupyter.notebook.insert_cell_below();
        Jupyter.notebook.select_next();
    }

    function jupyter_text2code_lib_callback(out_data) {
        if (out_data.msg_type === "execute_result"){
            var query = $("#jupyter_text2code_query").val();
            $.get({
                url: '/jupyter-text2code',
                data: {"query": query, "dataframes_info": out_data.content.data['text/plain']},
                beforeSend: function(){
                    $("#jupyter_text2code_loader").show();
                },
                success: function(response) {
                    code_exec_callback(query, response);
                },
                error: handle_jupyter_text2code_error,
                complete: function(){
                    $("#jupyter_text2code_loader").hide();
                },
            });
        }
    }

    function read_code_init(lib) {
        var libName = Jupyter.notebook.base_url + "nbextensions/jupyter-text2code/" + lib;
        $.get(libName).done(function(data) {
            jupyter_text2code_lib.code_init = data;
             requirejs(
             [],
            function() {
                Jupyter.notebook.kernel.execute(jupyter_text2code_lib.code_init, { iopub: { output: jupyter_text2code_lib_callback } }, { silent: false });
            })
            console.log(libName + ' loaded library');
        }).fail(function() {
            console.log(libName + 'failed to load ' + lib + ' library')
        });
    }

    var initialize = function () {
        Jupyter.toolbar.add_buttons_group([
            Jupyter.keyboard_manager.actions.register ({
                help   : 'Launch jupyter-text2code',
                icon   : 'fa-terminal',
                handler: toggle_jupyter_text2code_editor
            }, 'create-jupyter-text2code-from-notebook', 'Text2Code')
        ]);
        read_code_init("jupyter_text2code_lib.py");
    };

    function toggle_jupyter_text2code_editor() {
        if(extension_state.is_open) {
            extension_state.is_open = false;
            $(".jupyter_text2code_editor_display").hide();
        }
        else {
            if($('#jupyter_text2code_editor').length == 0) {
                build_jupyter_text2code_editor();
            }
            extension_state.is_open = true;
            $(".jupyter_text2code_editor_display").show();
        }
    }

    function build_alert(alert_class) {
        return $('<div/>')
            .addClass('alert alert-dismissable')
            .addClass(alert_class)
            .append(
                $('<button class="close" type="button" data-dismiss="alert" aria-label="Close"/>')
                    .append($('<span aria-hidden="true"/>').html('&times;'))
            );
    }

    function handle_jupyter_text2code_error(jqXHR, textStatus, errorThrown) {
        console.log('jupyter_text2code ajax error:', jqXHR, textStatus, errorThrown);
        var alert = build_alert('alert-danger')
            .hide()
            .append(
                $('<p/>').text('Error:')
            )
            .append(
                $('<pre/>').text(jqXHR.responseJSON ? JSON.stringify(jqXHR.responseJSON, null, 2) : errorThrown)
            );
        $('#jupyter_text2code_modal').find('.modal-body').append(alert);
        alert.slideDown('fast');
    }


    function add_presets(jupyter_text2code_editor) {

        var jupyter_text2code_preset = jupyter_text2code_editor.find('#jupyter_text2code_preset_content');
        extension_state.data.presets.forEach(function(item, index) {
            jupyter_text2code_preset.append("<div class='jupyter_text2code_preset_item'>"+ item + "</div>");
        });
        return jupyter_text2code_editor;
    }

    function update_history_display(query) {
        var jupyter_text2code_history = $('#jupyter_text2code_history');
            jupyter_text2code_history.prepend("<div class='jupyter_text2code_history_item'>"+ query + "</div>");
    }

    function build_jupyter_text2code_editor () {
        var jupyter_text2code_editor = $('<div/>').attr('id', 'jupyter_text2code_editor').attr('class', 'jupyter_text2code_editor_display');
        var jupyter_text2code_editor_history = $('<div/>').attr('id', 'jupyter_text2code_editor_history').attr('class', 'jupyter_text2code_editor_display');

        var textArea = $('<textarea id="jupyter_text2code_query"  class="form-control" />').val(extension_state.data.query).addClass('form-control');

        jupyter_text2code_editor
            .append("<div class='jupyter_text2code_what_heading'>What do you want to do?</div>")
            .append(textArea)
            .append("<button class='btn-primary' id='jupyter_text2code_submit'>Text2Code</button>")
            .append("<button id='jupyter_text2code_close'> Close </button>")
            .append("<div id='jupyter_text2code_loader' class='fa fa-spinner fa-spin fa-3x jupyter_text2code_spinner' style='display: none;'></div>");

        // History section
        jupyter_text2code_editor_history.append(""
           + "<div class='jupyter_text2code_sub_heading'>Command History:</div> <div id='jupyter_text2code_history_wrapper'><div id='jupyter_text2code_history'> </div></div>"
           + "<hr><div class='jupyter_text2code_sub_heading'>Presets:</div><div id='jupyter_text2code_preset_wrapper'><div id='jupyter_text2code_preset_content'></div></div>"
        );

        jupyter_text2code_editor_history = add_presets(jupyter_text2code_editor_history);

        // Close button click event handler
        $('body').on('click', '#jupyter_text2code_close', function() {
            extension_state.is_open = false;
            $(".jupyter_text2code_editor_display").hide();
        });
        // jupyter_text2code button click event handler
        $('body').on('click', '#jupyter_text2code_submit', function() {
            make_jupyter_text2code();
        });


        // Disable jupyter shortcuts while query is being typed(to avoid them from triggering)
        $('body').on('focus', '#jupyter_text2code_query', function() {
            Jupyter.keyboard_manager.disable();
        });
        $('body').on('blur', '#jupyter_text2code_query', function() {
            Jupyter.keyboard_manager.enable();
        });

        // Handler for clicking history item
        $('body').on('click', '.jupyter_text2code_history_item', function() {
            $("#jupyter_text2code_query").val($(this).text());
        });
        // Handler for clicking preset item
        $('body').on('click', '.jupyter_text2code_preset_item', function() {
            $("#jupyter_text2code_query").val($(this).text());
        });
        
        $("#notebook-container").append(jupyter_text2code_editor);
        $("body").append(jupyter_text2code_editor_history);
    }

    var make_jupyter_text2code = function make_jupyter_text2code() {
        var jupyter_text2code_lib_cmd = "dataframes_info()";
        requirejs([],
            function() {
                Jupyter.notebook.kernel.execute(
                    jupyter_text2code_lib_cmd, { iopub: { output: jupyter_text2code_lib_callback } }, { silent: false }
                );
            });
    };

    function load_jupyter_extension () {
        var link = document.createElement("link");
        link.type = "text/css";
        link.rel = "stylesheet";
        link.href = requirejs.toUrl("./jupyter_text2code.css");
        document.getElementsByTagName("head")[0].appendChild(link);

        // load when the kernel's ready
        if (Jupyter.notebook.kernel) {
          initialize();
        } else {
          events.on('kernel_ready.Kernel', initialize);
        }
        // return Jupyter.notebook.config.loaded.then(initialize);
    }

    return {
        load_jupyter_extension: load_jupyter_extension,
        load_ipython_extension: load_jupyter_extension
    };
});
