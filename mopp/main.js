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

    var mopp_lib = {}
    mopp_lib.code_init = "";

    // define default values for config parameters
    var params = {
        mopp_it_default_to_public: false,
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

    function mopp_lib_callback(out_data) {
        if (out_data.msg_type === "execute_result"){
            var query = $("#mopp_query").val();
            $.get({
                url: '/mopp',
                data: {"query": query, "dataframes_info": out_data.content.data['text/plain']},
                beforeSend: function(){
                    $("#mopp_loader").show();
                },
                success: function(response) {
                    code_exec_callback(query, response);
                },
                error: handle_mopp_error,
                complete: function(){
                    $("#mopp_loader").hide();
                },
            });
        }
    }

    function read_code_init(lib) {
        var libName = Jupyter.notebook.base_url + "nbextensions/mopp/" + lib;
        $.get(libName).done(function(data) {
            mopp_lib.code_init = data;
             requirejs(
             [],
            function() {
                Jupyter.notebook.kernel.execute(mopp_lib.code_init, { iopub: { output: mopp_lib_callback } }, { silent: false });
            })
            console.log(libName + ' loaded library');
        }).fail(function() {
            console.log(libName + 'failed to load ' + lib + ' library')
        });
    }

    var initialize = function () {
        Jupyter.toolbar.add_buttons_group([
            Jupyter.keyboard_manager.actions.register ({
                help   : 'Launch Mopp',
                icon   : 'fa-terminal',
                handler: toggle_mopp_editor
            }, 'create-mopp-from-notebook', 'mopp_it')
        ]);
        read_code_init("mopp_lib.py");
    };

    function toggle_mopp_editor() {
        if(extension_state.is_open) {
            extension_state.is_open = false;
            $(".mopp_editor_display").hide();
        }
        else {
            if($('#mopp_editor').length == 0) {
                build_mopp_editor();
            }
            extension_state.is_open = true;
            $(".mopp_editor_display").show();
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

    function handle_mopp_error(jqXHR, textStatus, errorThrown) {
        console.log('mopp ajax error:', jqXHR, textStatus, errorThrown);
        var alert = build_alert('alert-danger')
            .hide()
            .append(
                $('<p/>').text('Error:')
            )
            .append(
                $('<pre/>').text(jqXHR.responseJSON ? JSON.stringify(jqXHR.responseJSON, null, 2) : errorThrown)
            );
        $('#mopp_modal').find('.modal-body').append(alert);
        alert.slideDown('fast');
    }


    function add_presets(mopp_editor) {

        var mopp_preset = mopp_editor.find('#mopp_preset_content');
        extension_state.data.presets.forEach(function(item, index) {
            mopp_preset.append("<div class='mopp_preset_item'>"+ item + "</div>");
        });
        return mopp_editor;
    }

    function update_history_display(query) {
        var mopp_history = $('#mopp_history');
            mopp_history.prepend("<div class='mopp_history_item'>"+ query + "</div>");
    }

    function build_mopp_editor () {
        var mopp_editor = $('<div/>').attr('id', 'mopp_editor').attr('class', 'mopp_editor_display');
        var mopp_editor_history = $('<div/>').attr('id', 'mopp_editor_history').attr('class', 'mopp_editor_display');

        var textArea = $('<textarea id="mopp_query"  class="form-control" />').val(extension_state.data.query).addClass('form-control'); 

        mopp_editor
            .append("<div class='mopp_what_heading'>What do you want to do?</div>")
            .append(textArea)
            .append("<button class='btn-primary' id='mopp_submit'>mopp it!</button>")
            .append("<button id='mopp_close'> Close </button>")
            .append("<div id='mopp_loader' class='fa fa-spinner fa-spin fa-3x mopp_spinner' style='display: none;'></div>");

        // History section
        mopp_editor_history.append("" 
           + "<div class='mopp_sub_heading'>Command History:</div> <div id='mopp_history_wrapper'><div id='mopp_history'> </div></div>"
           + "<hr><div class='mopp_sub_heading'>Presets:</div><div id='mopp_preset_wrapper'><div id='mopp_preset_content'></div></div>"
        );

        mopp_editor_history = add_presets(mopp_editor_history);

        // Close button click event handler
        $('body').on('click', '#mopp_close', function() {
            extension_state.is_open = false;
            $(".mopp_editor_display").hide();
        });
        // Mopp button click event handler
        $('body').on('click', '#mopp_submit', function() {
            make_mopp();
        });


        // Disable jupyter shortcuts while query is being typed(to avoid them from triggering)
        $('body').on('focus', '#mopp_query', function() {
            Jupyter.keyboard_manager.disable();
        });
        $('body').on('blur', '#mopp_query', function() {
            Jupyter.keyboard_manager.enable();
        });

        // Handler for clicking history item
        $('body').on('click', '.mopp_history_item', function() {
            $("#mopp_query").val($(this).text());
        });
        // Handler for clicking preset item
        $('body').on('click', '.mopp_preset_item', function() {
            $("#mopp_query").val($(this).text());
        });
        
        $("#notebook-container").append(mopp_editor);
        $("body").append(mopp_editor_history);
    }

    var make_mopp = function make_mopp() {
        var mopp_lib_cmd = "dataframes_info()";
        requirejs([],
            function() {
                Jupyter.notebook.kernel.execute(
                    mopp_lib_cmd, { iopub: { output: mopp_lib_callback } }, { silent: false }
                );
            });
    };

    function load_jupyter_extension () {
        var link = document.createElement("link");
        link.type = "text/css";
        link.rel = "stylesheet";
        link.href = requirejs.toUrl("./mopp.css");
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
