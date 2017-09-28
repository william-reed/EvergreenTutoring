// Evergreen Tutoring - A simple online tutor scheduling service
// Copyright (C) 2017 William Reed
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>

/**
 * Char Counter 1.0.0
 * A simple character counter
 * @author William Reed
 * @requires jQuery
 */
(function ($) {

    $.fn.charCount = function (options) {

        var settings = $.extend({
            // These are the defaults.
            textAreaId: 'id_text_area',
            remainingMessage: " characters remaining"
        }, options);

        var textArea = $('#' + settings.textAreaId);
        var counter = $(this);
        var maxlength = textArea.attr('maxlength');
        if (textArea.html() !== "") {
            updateCharCount()
        } else {
            counter.html(maxlength + ' characters remaining');
        }

        textArea.keyup(updateCharCount);

        function updateCharCount() {
            var char_count = textArea.val().length;
            var chars_remaining = maxlength - char_count;

            counter.html(chars_remaining + ' characters remaining')
        }

        return this;
    };

}(jQuery));